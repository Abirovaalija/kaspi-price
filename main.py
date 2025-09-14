from flask import Flask, Response
import requests
import csv
import io
from datetime import datetime
import html

app = Flask(__name__)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQgg_vbcJzq_IOqPNPbuTyuLfb1xvapOCP3nTQlfzNmcRj7wh9kyT1oyZJx2W5MSFmPBZeP5T133pj_/pub?output=csv"
MERCHANT_ID = "16157146"

@app.route("/price.xml")
def price():
    response = requests.get(CSV_URL)
    response.encoding = "utf-8"
    csv_file = io.StringIO(response.text)
    reader = csv.DictReader(csv_file)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    xml_parts = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<kaspi_catalog date="{now}" xmlns="kaspiShopping" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="kaspiShopping http://kaspi.kz/kaspishopping.xsd">',
        f'  <company>{MERCHANT_ID}</company>',
        f'  <merchantid>{MERCHANT_ID}</merchantid>',
        '  <offers>'
    ]

    for row in reader:
        sku = row.get("SKU", "").strip()
        model = html.escape(row.get("model", "").strip())
        brand = html.escape(row.get("brand", "").strip() or "Без бренда")
        price = row.get("price", "").strip()

        availabilities = []
        for i in range(1, 6):
            stock = row.get(f"PP{i}", "").strip()
            pre_order = row.get("preOrder", "0").strip()

            if stock and stock.isdigit() and int(stock) > 0:
                avail = f'<availability available="yes" storeId="{MERCHANT_ID}_PP{i}" preOrder="{pre_order}" stockCount="{stock}"/>'
            else:
                avail = f'<availability available="no" storeId="{MERCHANT_ID}_PP{i}" preOrder="{pre_order}" stockCount="0"/>'
            availabilities.append(avail)

        offer_xml = f"""
    <offer sku="{sku}">
      <model>{model}</model>
      <brand>{brand}</brand>
      <availabilities>
        {' '.join(availabilities)}
      </availabilities>
      <price>{price}</price>
    </offer>"""
        xml_parts.append(offer_xml)

    xml_parts.append("  </offers>")
    xml_parts.append("</kaspi_catalog>")

    xml_content = "\n".join(xml_parts)
    return Response(xml_content, mimetype="application/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
