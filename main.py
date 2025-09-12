from flask import Flask, Response
import requests
import csv
import io

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
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<kaspi_catalog date="2025-09-12">\n  <company>Мой магазин</company>\n  <merchantid>12345</merchantid>\n  <offers>\n'

    for row in reader:
        xml += f'''    <offer sku="{row["sku"]}">
      <model>{row["name"]}</model>
      <brand>{row["brand"]}</brand>
      <price>{row["price"]}</price>
      <storeId>{row["storeId"]}</storeId>
    </offer>\n'''

    xml += "  </offers>\n</kaspi_catalog>"

    return Response(xml, mimetype='application/xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
