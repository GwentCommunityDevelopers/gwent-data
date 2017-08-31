#!/usr/bin/python3
import xml.etree.ElementTree as xml
import sys
import os
import Utils

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
        keywords[keywordId]['unformatted'] = Utils.cleanHtml(keywords[keywordId]['raw'])

    return keywords

def createKeywordJson():
    keywords = {}
    for locale in Utils.LOCALES:
        localisedKeywords = getKeywords(locale)
        keywords[locale] = localisedKeywords

    Utils.saveJson(xml_folder + "../keywords.json", keywords)

xml_folder = sys.argv[1]

# Add a backslash on the end if it doesn't exist.
if xml_folder[-1] != "/":
    xml_folder = xml_folder + "/"

if not os.path.isdir(xml_folder):
    print(xml_folder + " is not a valid directory")
    exit()

LOCALES = ["en-US"] #, "de-DE", "es-ES", "es-MX", "fr-FR", "it-IT", "ja-JP", "pl-PL", "pt-BR", "ru-RU", "zh-CN", "zh-TW"

createKeywordJson()
