from flask import Flask, Response
import requests
import csv
import io
import html
from datetime import datetime

app = Flask(__name__)

# Ссылка на Google Sheets (CSV)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQgg_vbcJzq_IOqPNPbuTyuLfb1xvapOCP3nTQlfzNmcRj7wh9kyT1oyZJx2W5MSFmPBZeP5T133pj_/pub?gid=1749981972&single=true&output=csv"

# ID магазина (Феникс)
MERCHANT_ID = "16157146"

@app.route('/')
def home():
    return "Сервер работает ✅. Прайс доступен по адресу /price.xml"

@app.route('/price.xml')
def price_xml():
    # Загружаем CSV
    response = requests.get(CSV_URL)
    response.encoding = 'utf-8'
    csv_data = response.text

    reader = csv.DictReader(io.StringIO(csv_data))

    # Текущее время
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Формируем XML
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
        preorder_val = row.get("preOrder", "").strip() or "0"

        # --- availabilities ---
        availabilities = []
        for i in range(1, 6):  # PP1 … PP5
            stock_raw = row.get(f"PP{i}", "").strip()
            stock_count = int(stock_raw) if stock_raw.isdigit() else 0

            available = "yes" if stock_count > 0 else "no"

            availabilities.append(
                f'<availability available="{available}" storeId="{MERCHANT_ID}_PP{i}" preOrder="{preorder_val}" stockCount="{stock_count}"/>'
            )

        availabilities_xml = "\n      ".join(availabilities)

        # --- offer ---
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
