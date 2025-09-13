from flask import Flask, Response
import requests
import csv
import io
import html
from datetime import datetime

app = Flask(__name__)

# Ссылка на Google Sheets в формате CSV
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQgg_vbcJzq_IOqPNPbuTyuLfb1xvapOCP3nTQlfzNmcRj7wh9kyT1oyZJx2W5MSFmPBZeP5T133pj_/pub?gid=1749981972&single=true&output=csv"

# ID магазина Феникс
MERCHANT_ID = "16157146"

@app.route('/')
def home():
    return "Сервер работает ✅. Данные доступны по адресу /price.xml"

@app.route('/price.xml')
def price_xml():
    # Загружаем CSV из Google Sheets
    response = requests.get(CSV_URL)
    response.encoding = 'utf-8'
    csv_data = response.text

    # Читаем CSV построчно
    reader = csv.DictReader(io.StringIO(csv_data))

    # Текущее время для атрибута date
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Формируем XML по формату Каспи
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += f'<kaspi_catalog xmlns="kaspiShopping" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    xml += f'xsi:schemaLocation="http://kaspi.kz/kaspishopping.xsd" date="{date_now}">\n'
    xml += f'  <company>{MERCHANT_ID}</company>\n'
    xml += f'  <merchantid>{MERCHANT_ID}</merchantid>\n'
    xml += '  <offers>\n'

    for row in reader:
        sku = html.escape(row.get("SKU", "").strip())
        model = html.escape(row.get("model", "").strip())
        brand = html.escape(row.get("brand", "").strip())
        price = row.get("price", "").strip() or "0"

        # Составляем availabilities
        availabilities = []
        for i in range(1, 6):  # PP1 … PP5
            store_suffix = f"PP{i}"
            stock_raw = row.get(f"PP{i}", "").strip()
            stock_count = row.get(f"stockCount{i}", "0").strip() or "0.0"

            # stockCount с десятичной точкой
            if "." not in stock_count:
                stock_count += ".0"

            if stock_raw and float(stock_count) > 0:
                availabilities.append(
                    f'<availability available="yes" storeId="{MERCHANT_ID}_{store_suffix}" preOrder="0" stockCount="{stock_count}"/>'
                )
            elif stock_raw:
                availabilities.append(
                    f'<availability available="no" storeId="{MERCHANT_ID}_{store_suffix}" preOrder="0" stockCount="{stock_count}"/>'
                )

        # Если нет складов вообще, добавляем один с available="no"
        if not availabilities:
            availabilities.append(
                f'<availability available="no" storeId="{MERCHANT_ID}_PP1" preOrder="0" stockCount="0.0"/>'
            )

        availabilities_xml = "\n      ".join(availabilities)

        xml += f'''    <offer sku="{sku}">
      <model>{model}</model>
      <brand>{brand}</brand>
      <availabilities>
      {availabilities_xml}
      </availabilities>
      <price>{price}</price>
    </offer>\n'''

    xml += "  </offers>\n</kaspi_catalog>"

    return Response(xml, mimetype='application/xml')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
