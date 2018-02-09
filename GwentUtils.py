#!/usr/bin/python3
import json
import re
import os

import xml.etree.ElementTree as xml
from pprint import pprint

LOCALES = ["en-US", "de-DE", "es-ES", "es-MX", "fr-FR", "it-IT", "ja-JP", "ko-KR", "pl-PL", "pt-BR", "ru-RU", "zh-CN", "zh-TW"]
LOCALISATION_FILE_NAMES = {
    "en-US": "en_us.csv",
    "de-DE": "de_de.csv",
    "es-ES": "es_es.csv",
    "es-MX": "es_mx.csv",
    "fr-FR": "fr_fr.csv",
    "it-IT": "it_it.csv",
    "ja-JP": "jp_jp.csv",
    "ko-KR": "kr_kr.csv",
    "pl-PL": "pl_pl.csv",
    "pt-BR": "pt_br.csv",
    "ru-RU": "ru_ru.csv",
    "zh-CN": "zh_cn.csv",
    "zh-TW": "zh_tw.csv"
}


def save_json(filepath, data):
    print("Saved JSON to: %s" % filepath)
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, sort_keys=True, indent=2, separators=(',', ': '))


def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def _is_token_valid(token, tooltips):
    if token is not None and token.find('Tooltip') is not None:
        valid = True
        for locale in LOCALES:
            tooltip = tooltips[locale].get(token.find('Tooltip').attrib['key'])
            if tooltip is None or tooltip == '':
                valid = False
        return valid
    else:
        return False


def _get_evaluated_tooltips(raw_tooltips, card_names, card_abilities):
    # Generate complete tooltips from the raw_tooltips and accompanying data.
    tooltips = {}
    for card_id in raw_tooltips:
        # Some cards don't have info.
        if raw_tooltips.get(card_id) is None or raw_tooltips.get(card_id) == "":
            tooltips[card_id] = ""
            continue

        # Set tooltip to be the raw tooltip string.
        tooltips[card_id] = raw_tooltips[card_id]
        # Regex. Get all strings that lie between a '{' and '}'.
        result = re.findall(r'.*?\{(.*?)\}.*?', tooltips[card_id])
        for key in result:
            ability_value = _get_card_ability_value(card_abilities, card_id, key)
            if ability_value is not None:
                tooltips[card_id] = tooltips[card_id].replace("{" + key + "}", ability_value)

    return tooltips

def _get_card_ability_value(card_abilities, card_id, key):
    ability = card_abilities.get(card_id)
    if ability is None:
        return None
    ability_data = ability.find('TemporaryVariables')
    if ability_data is not None:
        for value in ability_data:
            if value.attrib['Name'] == key:
                return value.attrib['V']

def _get_tokens(card_templates, card_abilities):
    tokens = {}
    for card_id in card_templates:
        tokens[card_id] = []
        ability = card_abilities.get(card_id)
        if ability is None:
            continue
        ability_data = ability.find('TemporaryVariables')
        if ability_data is not None:
            for value in ability_data.iter("V"):
                if value.attrib.get('Type') == "CardDefinition":
                    tokens[card_id].append(value.attrib['TemplateId'])
    return tokens


def _get_keywords(tooltips):
    keywords_by_tooltip_id = {}
    for tooltip_id in tooltips:
        tooltip = tooltips[tooltip_id]
        keywords = []
        # Find all keywords in info string. E.g. find 'spawn' in '<keyword=spawn>'
        # Can just use en-US here. It doesn't matter, all regions will return the same result.
        result = re.findall(r'<keyword=([^>]+)>', tooltip)
        for key in result:
            if not key in keywords:
                keywords.append(key)

        keywords_by_tooltip_id[tooltip_id] = keywords
    return keywords_by_tooltip_id


class GwentDataHelper:
    def __init__(self, raw_folder):
        self._folder = raw_folder
        self.card_templates = self.get_card_templates()
        raw_tooltips = {}
        self.card_names = {}
        self.flavor_strings = {}
        self.categories = {}
        for locale in LOCALES:
            raw_tooltips[locale] = self.get_card_tooltips(locale)
            self.card_names[locale] = self.get_card_names(locale)
            self.flavor_strings[locale] = self.get_flavor_strings(locale)
            self.categories[locale] = self.get_categories(locale)
        card_abilities = self.get_card_abilities()

        self.tooltips = {}
        for locale in LOCALES:
            self.tooltips[locale] = _get_evaluated_tooltips(raw_tooltips[locale], self.card_names[locale], card_abilities)

        # Can use any locale here, all locales will return the same result.
        self.keywords = _get_keywords(self.tooltips[LOCALES[0]])

        self.tokens = _get_tokens(self.card_templates, card_abilities)

    def get_tooltips_file(self, locale):
        path = self._folder + LOCALISATION_FILE_NAMES[locale]
        if not os.path.isfile(path):
            print("Couldn't find " + locale + " tooltips at " + path)
            exit()
        return path

    def get_card_tooltips(self, locale):
        tooltips_file = open(self.get_tooltips_file(locale), "r", encoding="utf-8")
        tooltips = {}
        tooltip_id = None
        for line in tooltips_file:
            if line[0] == "\"":
                # If the previous tooltip has not carried onto a new line.
                split = line.split("\";\"")
                if len(split) < 3 or "tooltip" not in split[0]:
                    continue
                tooltip_id = split[1].replace("_tooltip", "").replace("\"", "").lstrip("0")

                # Remove any quotation marks and new lines.
                tooltips[tooltip_id] = split[2].replace("\"\n", "").replace("\\n", "\n")
            elif tooltip_id != None:
                tooltips[tooltip_id] += line.replace("\"\n", "").replace("\\n", "\n")
        tooltips_file.close()
        return tooltips

    def get_keyword_tooltips(self, locale):
        tooltips_file = open(self.get_tooltips_file(locale), "r", encoding="utf-8")
        keywords = {}
        for tooltip in tooltips_file:
            split = tooltip.split("\";\"")
            if len(split) < 3 or "keyword" not in split[1]:
                continue
            keyword_id = split[1].replace("keyword_", "").replace("\"", "")

            keywords[keyword_id] = {}
            # Remove any quotation marks and new lines.
            keywords[keyword_id] = split[2].replace("\"", "").replace("\n", "")

        tooltips_file.close()
        return keywords

    def get_categories(self, locale):
        tooltips_file = open(self.get_tooltips_file(locale), "r", encoding="utf-8")
        categories = {}
        for line in tooltips_file:
            split = line.split("\";\"")
            if len(split) < 3 or "category" not in split[1]:
                continue
            category_id = split[1]

            categories[category_id] = {}
            # Remove any quotation marks and new lines.
            categories[category_id] = split[2].replace("\"", "").replace("\n", "")

        tooltips_file.close()
        return categories

    def get_card_templates(self):
        path = self._folder + "Templates.xml"
        if not os.path.isfile(path):
            print("Couldn't find templates.xml at " + path)
            exit()

        card_templates = {}

        tree = xml.parse(path)
        root = tree.getroot()

        for template in root.iter('Template'):
            card_templates[template.attrib['Id']] = template

        return card_templates

    def get_card_abilities(self):
        path = self._folder + "Abilities.xml"
        if not os.path.isfile(path):
            print("Couldn't find abilities.xml at " + path)
            exit()

        abilities = {}

        tree = xml.parse(path)
        root = tree.getroot()

        for ability in root.iter('Ability'):
            if ability.attrib['Type'] == "CardAbility":
                card_id = ability.attrib['Template']
                abilities[card_id] = ability

        return abilities

    def get_card_names(self, locale):
        card_name_file = open(self.get_card_names_file(locale), "r", encoding="utf8")
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
        card_name_file = open(self.get_card_names_file(locale), "r", encoding="utf8")
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
        path = self._folder + LOCALISATION_FILE_NAMES[locale]
        if not os.path.isfile(path):
            print("Couldn't find " + locale + " card file at " + path)
            exit()

        return path
