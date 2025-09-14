from flask import Flask, Response
import requests
import csv
import io
from datetime import datetime

app = Flask(__name__)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQgg_vbcJzq_IOqPNPbuTyuLfb1xvapOCP3nTQlfzNmcRj7wh9kyT1oyZJx2W5MSFmPBZeP5T133pj_/pub?output=csv"

@app.route('/price.xml')
def price_xml():
    response = requests.get(CSV_URL)
    response.encoding = "utf-8"
    csv_file = io.StringIO(response.text)
    reader = csv.DictReader(csv_file)

    xml = f'<?xml version="1.0" encoding="utf-8"?>\n'
    xml += f'<kaspi_catalog date="{datetime.now().strftime("%Y-%m-%d")}" xmlns="kaspiShopping" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
    xml += f'  <company>16157146</company>\n'
    xml += f'  <merchantid>16157146</merchantid>\n'
    xml += f'  <offers>\n'

    for row in reader:
        if not row.get("id") or not row.get("name") or not row.get("price"):
            continue  

        xml += f'    <offer sku="{row["id"]}">\n'
        xml += f'      <model>{row["name"]}</model>\n'
        xml += f'      <price>{row["price"]}</price>\n'
        xml += f'      <available>{row.get("available", "yes")}</available>\n'
        xml += f'      <quantity>{row.get("quantity", "1")}</quantity>\n'
        xml += f'    </offer>\n'

    xml += f'  </offers>\n'
    xml += f'</kaspi_catalog>\n'

    return Response(xml, mimetype='application/xml')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
