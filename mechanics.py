#!/usr/bin/python3
import xml.etree.ElementTree as xml
import sys
import os
import json
import re
import time
from pprint import pprint

def saveJson(filename, cardList):
    filepath = os.path.join(xml_folder + "../" + filename)
    print("Saving %s cards to: %s" % (len(cardList), filepath))
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cardList, f, sort_keys=True, indent=2, separators=(',', ': '))

def cleanHtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def getKeywords(locale):
    TOOLTIP_STRINGS_PATH = xml_folder + "tooltips_" + locale + ".csv"
    if not os.path.isfile(TOOLTIP_STRINGS_PATH):
        print("Couldn't find " + locale + " tooltips at " + TOOLTIP_STRINGS_PATH)
        exit()

    keywords = {}

    tooltipsFile = open(TOOLTIP_STRINGS_PATH, "r")
    for tooltip in tooltipsFile:
        split = tooltip.split("\";\"")
        if len(split) < 2:
            continue
        keywordId = split[1].replace("keyword_","").replace("\"", "")

        keywords[keywordId] = {}
        # Remove any quotation marks and new lines.
        keywords[keywordId]['raw'] = split[2].replace("\"", "").replace("\n", "")
        keywords[keywordId]['unformatted'] = cleanHtml(keywords[keywordId]['raw'])

    return keywords

def createKeywordJson():
    keywords = {}
    for locale in LOCALES:
        localisedKeywords = getKeywords(locale)
        keywords[locale] = localisedKeywords

    saveJson("keywords.json", keywords)

xml_folder = sys.argv[1]

# Add a backslash on the end if it doesn't exist.
if xml_folder[-1] != "/":
    xml_folder = xml_folder + "/"

if not os.path.isdir(xml_folder):
    print(xml_folder + " is not a valid directory")
    exit()

LOCALES = ["en-US"] #, "de-DE", "es-ES", "es-MX", "fr-FR", "it-IT", "ja-JP", "pl-PL", "pt-BR", "ru-RU", "zh-CN", "zh-TW"

createKeywordJson()
