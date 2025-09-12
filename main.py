from flask import Flask, Response
import requests
import csv
import io
import html

app = Flask(__name__)

# ссылка на твою Google таблицу в формате CSV
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQgg_vbcJzq_IOqPNPbuTyuLfb1xvapOCP3nTQlfzNmcRj7wh9kyT1oyZJx2W5MSFmPBZeP5T133pj_/pub?gid=1749981972&single=true&output=csv"

@app.route('/')
def home():
    return "Сервер работает ✅. Данные доступны по адресу /price.xml"

@app.route('/price.xml')
def price_xml():
    # загружаем CSV из Google Sheets
    response = requests.get(CSV_URL)
    response.encoding = 'utf-8'
    csv_data = response.text

    # читаем CSV построчно
    reader = csv.DictReader(io.StringIO(csv_data))

    # формируем XML
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
        preorder = row.get("preorder", "").strip()

        xml += f'    <offer sku="{sku}">\n'
        xml += f'      <model>{model}</model>\n'
        xml += f'      <brand>{brand}</brand>\n'
        xml += f'      <price>{price}</price>\n'

        # склады
        xml += '      <availabilities>\n'
        for store in ["PP1", "PP2", "PP3", "PP4", "PP5"]:
            if row.get(store, "").strip().lower() in ["yes", "да", "true", "1"]:
                xml += f'        <availability available="yes" storeId="{store}"/>\n'
            else:
                xml += f'        <availability available="no" storeId="{store}"/>\n'
        xml += '      </availabilities>\n'

        # предзаказ (если есть число)
        if preorder:
            xml += f'      <preOrder>{html.escape(preorder)}</preOrder>\n'

        xml += '    </offer>\n'

    xml += '  </offers>\n</kaspi_catalog>'

    return Response(xml, mimetype='application/xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
