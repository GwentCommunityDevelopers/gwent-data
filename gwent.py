#!/usr/bin/python3
import argparse
import os

import card_data
import mechanics
import utils

from datetime import datetime

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

# Save under v0-9-10_2017-09-05.json if the script is ran on 5 September 2017 with patch v0-9-10.
BASE_FILENAME = PATCH + "_" + datetime.utcnow().strftime("%Y-%m-%d") + ".json"

print("Creating keyword JSON...")
keywordsJson = mechanics.createKeywordJson(rawFolder)
filename = "keywords_" + BASE_FILENAME
filepath = os.path.join(rawFolder + "../" + filename)
utils.saveJson(filepath, keywordsJson)

print("Creating card data JSON...")
cardsJson = card_data.createCardJson(rawFolder, PATCH)
filename = "cards_" + BASE_FILENAME
filepath = os.path.join(rawFolder + "../" + filename)
print("Found %s cards." % (len(cardsJson)))
utils.saveJson(filepath, cardsJson)
