import csv
from io import StringIO

import requests
from lxml import etree

data = requests.get(
    "https://strommeninc.com/1000-most-common-italian-words-frequency-vocabulary-using-the-80-20-principle/"
).text

parser = etree.HTMLParser()

with StringIO(data) as file:
    root = etree.parse(file, parser)
category = root.xpath(
    "/html/body/div[1]/div[2]/div/div/main/div/section[1]/div/div/div/div[5]/div/div/section/div/div/div/div[1]/div/table[1]/tbody/tr"
)

with open("data/dict.csv", "w") as of:
    writer = csv.writer(of)
    writer.writerow(["rank", "italian", "english"])
    for row in category:
        writer.writerow([c.text for c in row.getchildren()])
