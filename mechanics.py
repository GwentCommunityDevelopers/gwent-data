#!/usr/bin/python3
import xml.etree.ElementTree as xml
import sys
import os
import utils
from datetime import datetime

def getKeywords(locale):
    TOOLTIP_STRINGS_PATH = xml_folder + "tooltips_" + locale + ".csv"
    if not os.path.isfile(TOOLTIP_STRINGS_PATH):
        print("Couldn't find " + locale + " tooltips at " + TOOLTIP_STRINGS_PATH)
        exit()

    keywords = {}

    tooltipsFile = open(TOOLTIP_STRINGS_PATH, "r")
    for tooltip in tooltipsFile:
        split = tooltip.split("\";\"")
        if len(split) < 2 or "keyword" not in split[1]:
            continue
        keywordId = split[1].replace("keyword_","").replace("\"", "")

        keywords[keywordId] = {}
        # Remove any quotation marks and new lines.
        keywords[keywordId]['raw'] = split[2].replace("\"", "").replace("\n", "")
        keywords[keywordId]['unformatted'] = utils.cleanHtml(keywords[keywordId]['raw'])

    return keywords

def createKeywordJson():
    keywords = {}
    for locale in utils.LOCALES:
        localisedKeywords = getKeywords(locale)
        keywords[locale] = localisedKeywords

    filename = "keywords_" + datetime.utcnow().strftime("%Y-%m-%d") + ".json"
    filepath = os.path.join(xml_folder + "../" + filename)
    utils.saveJson(filepath, keywords)

xml_folder = sys.argv[1]

# Add a backslash on the end if it doesn't exist.
if xml_folder[-1] != "/":
    xml_folder = xml_folder + "/"

if not os.path.isdir(xml_folder):
    print(xml_folder + " is not a valid directory")
    exit()

createKeywordJson()
