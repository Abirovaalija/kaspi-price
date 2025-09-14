from flask import Flask, Response
import requests
import csv
import io
from datetime import datetime
import html

app = Flask(__name__)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQgg_vbcJzq_IOqPNPbuTyuLfb1xvapOCP3nTQlfzNmcRj7wh9kyT1oyZJx2W5MSFmPBZeP5T133pj_/pub?output=csv"

MERCHANT_ID = "16157146"  # Феникс

@app.route("/price.xml")
def price():
    response = requests.get(CSV_URL)
    response.encoding = "utf-8"
    csv_file = io.StringIO(response.text)
    reader = csv.DictReader(csv_file)

    today = datetime.today().strftime("%Y-%m-%d")

    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += f'<kaspi_catalog xmlns="http://kaspi.kz/kaspishopping" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" date="{today}">\n'
    xml += f'  <company>{MERCHANT_ID}</company>\n'
    xml += f'  <merchantid>{MERCHANT_ID}</merchantid>\n'
    xml += f'  <offers>\n'

    for row in reader:
        sku = html.escape(row["SKU"].strip())
        model = html.escape(row["model"].strip())
        brand = html.escape(row["brand"].strip())
        price = row["price"].strip()
        preorder = row.get("preOrder", "0").strip()

        if not sku or not model or not brand or not price:
            continue  # пропускаем пустые строки

        xml += f'    <offer sku="{sku}">\n'
        xml += f'      <model>{model}</model>\n'
        xml += f'      <brand>{brand}</brand>\n'

        xml += f'      <availabilities>\n'
        for i in range(1, 6):
            stock = row.get(f"PP{i}", "").strip()
            if stock.isdigit():
                available = "yes" if int(stock) > 0 else "no"
                xml += f'        <availability available="{available}" storeId="{MERCHANT_ID}_PP{i}" preOrder="{preorder}" stockCount="{stock}"/>\n'
        xml += f'      </availabilities>\n'

        xml += f'      <cityprices>\n'
        xml += f'        <cityprice cityId="710000000">{price}</cityprice>\n'
        xml += f'      </cityprices>\n'

        xml += f'    </offer>\n'

    xml += f'  </offers>\n'
    xml += f'</kaspi_catalog>'

    return Response(xml, mimetype="application/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
