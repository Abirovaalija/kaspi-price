from flask import Flask, Response
import requests
import csv
import io
import html

app = Flask(__name__)

# Ссылка на Google Sheets в формате CSV
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQgg_vbcJzq_IOqPNPbuTyuLfb1xvapOCP3nTQlfzNmcRj7wh9kyT1oyZJx2W5MSFmPBZeP5T133pj_/pub?gid=1749981972&single=true&output=csv"

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

    # Формируем XML по формату Каспи
    xml = '<?xml version="1.0" encoding="utf-8"?>\n'
    xml += '<kaspi_catalog date="2025-09-12" xmlns="kaspiShopping" '
    xml += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    xml += 'xsi:schemaLocation="kaspiShopping http://kaspi.kz/kaspishopping.xsd">\n'
    xml += f'  <company>Феникс</company>\n'
    xml += f'  <merchantid>16157146</merchantid>\n'
    xml += '  <offers>\n'

    for row in reader:
        sku = html.escape(row.get("SKU", "").strip())
        model = html.escape(row.get("model", "").strip())
        brand = html.escape(row.get("brand", "").strip())
        price = html.escape(row.get("price", "").strip())

        # Составляем availabilities
        availabilities = []
        for i in range(1, 6):  # PP1 … PP5
            store_id = row.get(f"PP{i}", "").strip()
            if store_id and store_id != "0":
                pre_order = row.get("preorder", "0").strip()  # если есть предзаказ
                stock_count = row.get(f"stockCount{i}", "0").strip()  # если есть количество
                availabilities.append(f'<availability available="yes" storeId="{store_id}" preOrder="{pre_order}" stockCount="{stock_count}"/>')

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