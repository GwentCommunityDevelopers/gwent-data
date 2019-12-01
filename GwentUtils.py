#!/usr/bin/python3
import json
import re
import os

import xml.etree.ElementTree as xml
from pprint import pprint

LOCALES = ["en-US", "de-DE", "es-ES", "es-MX", "fr-FR", "it-IT", "ja-JP", "ko-KR", "pl-PL", "pt-BR", "ru-RU", "zh-CN", "zh-TW"]
LOCALISATION_FILE_NAMES = {
    "en-US": "Localization/en-us.csv",
    "de-DE": "Localization/de-de.csv",
    "es-ES": "Localization/es-es.csv",
    "es-MX": "Localization/es-mx.csv",
    "fr-FR": "Localization/fr-fr.csv",
    "it-IT": "Localization/it-it.csv",
    "ja-JP": "Localization/ja-jp.csv",
    "ko-KR": "Localization/ko-kr.csv",
    "pl-PL": "Localization/pl-pl.csv",
    "pt-BR": "Localization/pt-br.csv",
    "ru-RU": "Localization/ru-ru.csv",
    "zh-CN": "Localization/zh-cn.csv",
    "zh-TW": "Localization/zh-tw.csv"
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


def _get_evaluated_tooltips(raw_tooltips, card_names, card_abilities, card_templates):
    # Generate complete tooltips from the raw_tooltips and accompanying data.
    tooltips = {}
    for card_id in raw_tooltips:

        # Some cards don't have info.
        if raw_tooltips.get(card_id) is None or raw_tooltips.get(card_id) == "":
            tooltips[card_id] = ""
            continue

        # Set tooltip to be the raw tooltip string.
        tooltips[card_id] = raw_tooltips[card_id]

        template = card_templates[card_id]
        # First replace the MaxRange placeholder
        result = re.findall(r'.*?(\{Card\.MaxRange\}).*?', tooltips[card_id])
        for key in result:
            value = template.find('MaxRange').text
            tooltips[card_id] = tooltips[card_id].replace(key, value)

        # Replace provision cost placeholder
        result = re.findall(r'.*?(\{Template\.Provision\}).*?', tooltips[card_id])
        for key in result:
            value = template.find('Provision').text
            tooltips[card_id] = tooltips[card_id].replace(key, value)

        # Now replace all the other card abilities.
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

    lower_case_key = key.lower()
    ability_data = ability.find('PersistentVariables')
    if ability_data is not None:
        for value in ability_data:
            if value.attrib['Name'].lower() == lower_case_key:
                return value.attrib['V']

    ability_data = ability.find('TemporaryVariables')
    if ability_data is not None:
        for value in ability_data:
            if value.attrib['Name'].lower() == lower_case_key:
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
                    token_id = value.attrib['TemplateId']
                    if token_id not in tokens[card_id]:
                        tokens[card_id].append(token_id)

                for child in value:
                    if child.attrib.get('Type') == "CardDefinition":
                        token_id = child.attrib['TemplateId']
                        if token_id not in tokens[card_id]:
                            tokens[card_id].append(token_id)
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
            self.tooltips[locale] = _get_evaluated_tooltips(raw_tooltips[locale], self.card_names[locale], card_abilities, self.card_templates)

        # Can use any locale here, all locales will return the same result.
        self.keywords = _get_keywords(self.tooltips[LOCALES[0]])

        self.tokens = _get_tokens(self.card_templates, card_abilities)

        self.artists = self.get_artists()

        self.armor = self.get_card_armor()

    def get_tooltips_file(self, locale):
        path = self._folder + LOCALISATION_FILE_NAMES[locale]
        if not os.path.isfile(path):
            print("Couldn't find " + locale + " tooltips at " + path)
            exit()
        return path

    def get_card_tooltips(self, locale):
        tooltips_file = open(self.get_tooltips_file(locale), "r", encoding="utf-8")
        tooltips = {}
        for line in tooltips_file:
            split = line.split(";", 1)
            if "tooltip" not in split[0]:
                continue
            tooltip_id = split[0].replace("_tooltip", "").replace("\"", "").lstrip("0")

            # Remove any weird tooltip ids e.g. 64_tooltip_lt
            if "_lt" in tooltip_id:
                continue

            # Remove any quotation marks and new lines.
            tooltips[tooltip_id] = split[1].replace("\"\n", "").replace("\\n", "\n")
        tooltips_file.close()
        return tooltips

    def get_keyword_tooltips(self, locale):
        tooltips_file = open(self.get_tooltips_file(locale), "r", encoding="utf-8")
        keywords = {}
        for tooltip in tooltips_file:
            split = tooltip.split(";", 1)
            if "keyword" not in split[0]:
                continue
            keyword_id = split[0].replace("keyword_", "").replace("\"", "")

            keywords[keyword_id] = {}
            # Remove any quotation marks and new lines.
            keywords[keyword_id] = split[1].replace("\"", "").replace("\n", "")

        tooltips_file.close()
        return keywords

    def get_categories(self, locale):
        tooltips_file = open(self.get_tooltips_file(locale), "r", encoding="utf-8")
        categories = {}
        for line in tooltips_file:
            split = line.split(";", 1)
            if "category" not in split[0]:
                continue
            category_id = split[0]

            categories[category_id] = {}
            # Remove any quotation marks and new lines.
            categories[category_id] = split[1].replace("\"", "").replace("\n", "")

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

    def get_artists(self):
        path = self._folder + "ArtDefinitions.xml"
        if not os.path.isfile(path):
            print("Couldn't find ArtDefinitions.xml at " + path)
            exit()

        artists = {}

        tree = xml.parse(path)
        root = tree.getroot()

        for art in root.iter('ArtDefinition'):
            art_id = art.attrib['ArtId']
            artist = art.get('ArtistName')
            if artist != None:
                artists[art_id] = artist

        return artists

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

    def get_card_armor(self):
        path = self._folder + "Abilities.xml"
        if not os.path.isfile(path):
            print("Couldn't find abilities.xml at " + path)
            exit()

        armor = {}

        tree = xml.parse(path)
        root = tree.getroot()

        for ability in root.iter('Ability'):
            card_id = None

            if ability.attrib['Type'] == "CardAbility":
                card_id = ability.attrib['Template']
            
            if card_id:
                for tempVar in ability.iter('TemporaryVariables'):
                    children = list(tempVar)

                    for child in children:
                        if (child.attrib['Name'] == "Armor"):
                            armor[card_id] = child.attrib['V']

        return armor

    def get_card_names(self, locale):
        card_name_file = open(self.get_card_names_file(locale), "r", encoding="utf8")
        card_names = {}
        for line in card_name_file:
            split = line.split(";", 1)
            if len(split) < 2:
                continue
            if "_name" in split[0]:
                name_id = split[0].replace("_name", "").replace("\"", "")
                # Remove any quotation marks and new lines.
                card_names[name_id] = split[1].replace("\"", "").replace("\n", "")

        card_name_file.close()
        return card_names

    def get_flavor_strings(self, locale):
        card_name_file = open(self.get_card_names_file(locale), "r", encoding="utf8")
        flavor_strings = {}
        for line in card_name_file:
            split = line.split(";", 1)
            if len(split) < 2:
                continue
            if "_fluff" in split[0]:
                flavor_id = split[0].replace("_fluff", "").replace("\"", "")
                # Remove any quotation marks and new lines.
                flavor_strings[flavor_id] = split[1].replace("\"", "").replace("\n", "")

        card_name_file.close()
        return flavor_strings

    def get_card_names_file(self, locale):
        path = self._folder + LOCALISATION_FILE_NAMES[locale]
        if not os.path.isfile(path):
            print("Couldn't find " + locale + " card file at " + path)
            exit()

        return path
