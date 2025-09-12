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

    # Формируем XML
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<kaspi_catalog date="2025-09-12">\n'
    xml += '  <company>Мой магазин</company>\n'
    xml += '  <merchantid>12345</merchantid>\n'
    xml += '  <offers>\n'

    for row in reader:
        sku = html.escape(row["SKU"])
        model = html.escape(row["model"])
        brand = html.escape(row["brand"])
        price = html.escape(row["price"])

        # склады
        stores = []
        for i in range(1, 6):  # PP1 … PP5
            if row.get(f"PP{i}", "").strip() and row[f"PP{i}"] != "0":
                stores.append(f"<storeId>PP{i}</storeId>")

        stores_xml = "\n".join(stores)

        # предзаказ
        preorder_val = row.get("preorder", "").strip()
        preorder_xml = f"<preorder>{html.escape(preorder_val)}</preorder>" if preorder_val else ""

        xml += f'''    <offer sku="{sku}">
      <model>{model}</model>
      <brand>{brand}</brand>
      <price>{price}</price>
      {stores_xml}
      {preorder_xml}
    </offer>\n'''

    xml += "  </offers>\n</kaspi_catalog>"

    return Response(xml, mimetype='application/xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
