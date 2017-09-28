#!/usr/bin/python3
import json
import re
import os

import xml.etree.ElementTree as xml

LOCALES = ["en-US", "de-DE", "es-ES", "es-MX", "fr-FR", "it-IT", "ja-JP", "pl-PL", "pt-BR", "ru-RU", "zh-CN", "zh-TW"]


def save_json(filepath, data):
    print("Saved JSON to: %s" % filepath)
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, sort_keys=True, indent=2, separators=(',', ': '))


def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


class GwentDataHelper:
    def __init__(self, raw_folder):
        self._folder = raw_folder

    def get_tooltips_file(self, locale):
        path = self._folder + "tooltips_" + locale + ".csv"
        if not os.path.isfile(path):
            print("Couldn't find " + locale + " tooltips at " + path)
            exit()
        return path

    def get_card_tooltips(self, locale):
        tooltips_file = open(self.getTooltipsFile(locale), "r")
        tooltips = {}
        for tooltip in tooltips_file:
            split = tooltip.split("\";\"")
            if len(split) < 2:
                continue
            tooltip_id = split[1].replace("tooltip_", "").replace("_description", "").replace("\"", "").lstrip("0")

            # Remove any quotation marks and new lines.
            tooltips[tooltip_id] = split[2].replace("\"\n", "").replace("\\n", "\n")

        tooltips_file.close()
        return tooltips

    def get_keyword_tooltips(self, locale):
        tooltips_file = open(self.getTooltipsFile(locale), "r")
        keywords = {}
        for tooltip in tooltips_file:
            split = tooltip.split("\";\"")
            if len(split) < 2 or "keyword" not in split[1]:
                continue
            keyword_id = split[1].replace("keyword_", "").replace("\"", "")

            keywords[keyword_id] = {}
            # Remove any quotation marks and new lines.
            keywords[keyword_id]['raw'] = split[2].replace("\"", "").replace("\n", "")
            keywords[keyword_id]['unformatted'] = clean_html(keywords[keyword_id]['raw'])

        tooltips_file.close()
        return keywords

    def get_card_templates(self):
        path = self._folder + "GwentCardTemplates.xml"
        if not os.path.isfile(path):
            print("Couldn't find templates.xml at " + path)
            exit()

        card_templates = {}

        tree = xml.parse(path)
        root = tree.getroot()

        for template in root.iter('CardTemplate'):
            card_templates[template.attrib['id']] = template

        return card_templates

    def get_card_abilities(self):
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

    def get_tooltip_data(self):
        path = self._folder + "GwentTooltips.xml"
        if not os.path.isfile(path):
            print("Couldn't find tooltips.xml at " + path)
            exit()

        tooltip_data = {}

        tree = xml.parse(path)
        root = tree.getroot()

        for tooltip in root.iter('CardTooltip'):
            tooltip_data[tooltip.attrib['id']] = tooltip

        return tooltip_data

    def get_card_names(self, locale):
        card_name_file = open(self.getCardNamesFile(locale), "r", encoding="utf8")
        card_names = {}
        for line in card_name_file:
            split = line.split(";")
            if len(split) < 2:
                continue
            if "_name" in split[1]:
                name_id = split[1].replace("_name", "").replace("\"", "")
                # Remove any quotation marks and new lines.
                card_names[name_id] = split[2].replace("\"", "").replace("\n", "")

        card_name_file.close()
        return card_names

    def get_flavor_strings(self, locale):
        card_name_file = open(self.getCardNamesFile(locale), "r", encoding="utf8")
        flavor_strings = {}
        for line in card_name_file:
            split = line.split(";")
            if len(split) < 2:
                continue
            if "_fluff" in split[1]:
                flavor_id = split[1].replace("_fluff", "").replace("\"", "")
                # Remove any quotation marks and new lines.
                flavor_strings[flavor_id] = split[2].replace("\"", "").replace("\n", "")

        card_name_file.close()
        return flavor_strings

    def get_card_names_file(self, locale):
        path = self._folder + "cards_" + locale + ".csv"
        if not os.path.isfile(path):
            print("Couldn't find " + locale + " card file at " + path)
            exit()

        return path
