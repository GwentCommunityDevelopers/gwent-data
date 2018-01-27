#!/usr/bin/python3
import argparse
import os
import GwentUtils

from datetime import datetime
import CardData
import KeywordData
import CategoryData

parser = argparse.ArgumentParser(description="Transform the Gwent card data contained in xml files into a "
                                             "standardised JSON format.",
                                 epilog="Usage example:\n./master_xml.py ./pathToXML v0-9-10",
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("inputFolder", help="Folder containing the xml files.")
parser.add_argument("patch", help="Specifies the Gwent patch version.")
args = parser.parse_args()
PATCH = args.patch
rawFolder = args.inputFolder

# Add a backslash on the end if it doesn't exist.
if rawFolder[-1] != "/":
    rawFolder = rawFolder + "/"

if not os.path.isdir(rawFolder):
    print(rawFolder + " is not a valid directory")
    exit()

gwentDataHelper = GwentUtils.GwentDataHelper(rawFolder)

# Save under v0-9-10_2017-09-05.json if the script is ran on 5 September 2017 with patch v0-9-10.
BASE_FILENAME = PATCH + "_" + datetime.utcnow().strftime("%Y-%m-%d") + ".json"

print("Creating keyword JSON...")
keywordsJson = KeywordData.create_keyword_json(gwentDataHelper)
filename = "keywords_" + BASE_FILENAME
filepath = os.path.join(rawFolder + "../" + filename)
GwentUtils.save_json(filepath, keywordsJson)

print("Creating categories JSON...")
categoriesJson = CategoryData.create_category_json(gwentDataHelper)
filename = "categories_" + BASE_FILENAME
filepath = os.path.join(rawFolder + "../" + filename)
GwentUtils.save_json(filepath, categoriesJson)

print("Creating card data JSON...")
cardsJson = CardData.create_card_json(gwentDataHelper, PATCH)
filename = "cards_" + BASE_FILENAME
filepath = os.path.join(rawFolder + "../" + filename)
print("Found %s cards." % (len(cardsJson)))
GwentUtils.save_json(filepath, cardsJson)
