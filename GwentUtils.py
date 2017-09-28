#!/usr/bin/python3
import json
import re
import os

import xml.etree.ElementTree as xml

LOCALES = ["en-US", "de-DE", "es-ES", "es-MX", "fr-FR", "it-IT", "ja-JP", "pl-PL", "pt-BR", "ru-RU", "zh-CN", "zh-TW"]

def saveJson(filepath, data):
    print("Saved JSON to: %s" % filepath)
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, sort_keys=True, indent=2, separators=(',', ': '))

def cleanHtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

class GwentDataHelper:
    def __init__(self, rawFolder):
        self._folder = rawFolder

    def getTooltipsFile(self, locale):
        path = self._folder + "tooltips_" + locale + ".csv"
        if not os.path.isfile(path):
            print("Couldn't find " + locale + " tooltips at " + path)
            exit()
        return path

    def getCardTooltips(self, locale):
        tooltipsFile = open(self.getTooltipsFile(locale), "r")
        tooltips = {}
        for tooltip in tooltipsFile:
            split = tooltip.split("\";\"")
            if len(split) < 2:
                continue
            tooltipId = split[1].replace("tooltip_","").replace("_description","").replace("\"", "").lstrip("0")

            # Remove any quotation marks and new lines.
            tooltips[tooltipId] = split[2].replace("\"\n", "").replace("\\n", "\n")

        tooltipsFile.close()
        return tooltips

    def getKeywordTooltips(self, locale):
        tooltipsFile = open(self.getTooltipsFile(locale), "r")
        keywords = {}
        for tooltip in tooltipsFile:
            split = tooltip.split("\";\"")
            if len(split) < 2 or "keyword" not in split[1]:
                continue
            keywordId = split[1].replace("keyword_","").replace("\"", "")

            keywords[keywordId] = {}
            # Remove any quotation marks and new lines.
            keywords[keywordId]['raw'] = split[2].replace("\"", "").replace("\n", "")
            keywords[keywordId]['unformatted'] = cleanHtml(keywords[keywordId]['raw'])

        tooltipsFile.close()
        return keywords

    def getCardTemplates(self):
        path = self._folder + "GwentCardTemplates.xml"
        if not os.path.isfile(path):
            print("Couldn't find templates.xml at " + path)
            exit()

        cardTemplates = {}

        tree = xml.parse(path)
        root = tree.getroot()

        for template in root.iter('CardTemplate'):
            cardTemplates[template.attrib['id']] = template

        return cardTemplates

    def getCardAbilities(self):
        path = self._folder + "GwentCardAbilities.xml"
        if not os.path.isfile(path):
            print("Couldn't find abilities.xml at " + path)
            exit()

        abilities = {}

        tree = xml.parse(path)
        root = tree.getroot()

        for ability in root.iter('Ability'):
            abilities[ability.attrib['id']] = ability

        return abilities

    def getTooltipData(self):
        path = self._folder + "GwentTooltips.xml"
        if not os.path.isfile(path):
            print("Couldn't find tooltips.xml at " + path)
            exit()

        tooltipData = {}

        tree = xml.parse(path)
        root = tree.getroot()

        for tooltip in root.iter('CardTooltip'):
            tooltipData[tooltip.attrib['id']] = tooltip

        return tooltipData

    def getCardNames(self, locale):
        cardNameFile = open(self.getCardNamesFile(locale), "r", encoding="utf8")
        cardNames = {}
        for line in cardNameFile:
            split = line.split(";")
            if len(split) < 2:
                continue
            if "_name" in split[1]:
                nameId = split[1].replace("_name", "").replace("\"", "")
                # Remove any quotation marks and new lines.
                cardNames[nameId] = split[2].replace("\"", "").replace("\n", "")

        cardNameFile.close()
        return cardNames

    def getFlavorStrings(self, locale):
        cardNameFile = open(self.getCardNamesFile(locale), "r", encoding="utf8")
        flavorStrings = {}
        for line in cardNameFile:
            split = line.split(";")
            if len(split) < 2:
                continue
            if "_fluff" in split[1]:
                flavorId = split[1].replace("_fluff", "").replace("\"", "")
                # Remove any quotation marks and new lines.
                flavorStrings[flavorId] = split[2].replace("\"", "").replace("\n", "")

        cardNameFile.close()
        return flavorStrings

    def getCardNamesFile(self, locale):
        path = self._folder + "cards_" + locale + ".csv"
        if not os.path.isfile(path):
            print("Couldn't find " + locale + " card file at " + path)
            exit()

        return path
