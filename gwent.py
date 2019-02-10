#!/usr/bin/python3
import argparse
import os
import sys
import GwentUtils

from datetime import datetime
import CardData
import KeywordData
import CategoryData

parser = argparse.ArgumentParser(description="Transform the Gwent card data contained in xml files into a "
                                             "standardised JSON format. See README for more info.",
                                 epilog="Usage example:\n./master_xml.py ./pathToXML v0-9-10",
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("inputFolder", help="unzipped data_definitions.zip. Folder containing the xml files.")
parser.add_argument("-p", "--patch", help="Specifies the Gwent patch version. Used to create image urls.")
parser.add_argument("-i", "--images", help="Base image url to use for card images. See README for more info.")
args = parser.parse_args()
patch = args.patch
rawFolder = args.inputFolder
base_image_url = args.images
if not base_image_url:
    base_image_url = "https://firebasestorage.googleapis.com/v0/b/gwent-9e62a.appspot.com/o/images%2F{patch}%2F{cardId}%2F{variationId}%2F{size}.png?alt=media"
    if not patch:
        exit("Error: If you are not supplying an image url, you need to specify the patch name using --patch.\n"
            "This is because the default image url uses the patch name to generate the image url.\n"
            "See README for more info.")
elif "{patch}" in base_image_url and not patch:
    exit("Your image url contains {patch} but you have not supplied a patch name using -p. See README for more info")

# Add a backslash on the end if it doesn't exist.
if rawFolder[-1] != "/":
    rawFolder = rawFolder + "/"

if not os.path.isdir(rawFolder):
    print(rawFolder + " is not a valid directory")
    exit()

gwentDataHelper = GwentUtils.GwentDataHelper(rawFolder)

# Save under v0-9-10_2017-09-05.json if the script is ran on 5 September 2017 with patch v0-9-10.
BASE_FILENAME = patch + "_" + datetime.utcnow().strftime("%Y-%m-%d") + ".json"

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
cardsJson = CardData.create_card_json(gwentDataHelper, patch, base_image_url)
filename = "cards_" + BASE_FILENAME
filepath = os.path.join(rawFolder + "../" + filename)
print("Found %s cards." % (len(cardsJson)))
GwentUtils.save_json(filepath, cardsJson)
