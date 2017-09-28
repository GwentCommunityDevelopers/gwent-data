#!/usr/bin/python3
import json
import re
import os

import xml.etree.ElementTree as xml
from pprint import pprint

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
        raw_tooltips = {}
        self.card_names = {}
        self.flavor_strings = {}
        for locale in LOCALES:
            raw_tooltips[locale] = self.get_card_tooltips(locale)
            self.card_names[locale] = self.get_card_names(locale)
            self.flavor_strings[locale] = self.get_flavor_strings(locale)
        tooltip_data = self.get_tooltip_data()
        card_abilities = self.get_card_abilities()

        self.tooltips = {}
        for locale in LOCALES:
            self.tooltips[locale] = self._get_evaluated_tooltips(raw_tooltips[locale], tooltip_data, self.card_names[locale], card_abilities)

        # Can use any locale here, all locales will return the same result.
        self.keywords = self._get_keywords(self.tooltips[LOCALES[0]])

    @staticmethod
    def _get_evaluated_tooltips(raw_tooltips, tooltip_data, card_names, card_abilities):
        # Generate complete tooltips from the raw_tooltips and accompanying data.
        tooltips = {}
        for tooltip_id in raw_tooltips:
            # Some cards don't have info.
            if raw_tooltips.get(tooltip_id) is None or raw_tooltips.get(tooltip_id) == "":
                continue

            # Set tooltip to be the raw tooltip string.
            tooltips[tooltip_id] = raw_tooltips[tooltip_id]
            # Regex. Get all strings that lie between a '{' and '}'.
            result = re.findall(r'.*?\{(.*?)\}.*?', tooltips[tooltip_id])
            card_data = tooltip_data.get(tooltip_id)
            if card_data is None:
                continue
            for key in result:
                for variable in card_data.iter('VariableData'):
                    data = variable.find(key)
                    if data is None:
                        # This is not the right variable for this key, let's check the next one.
                        continue
                    if "crd" in key:
                        # Spawn a specific card.
                        crd = data.attrib['V']
                        if crd != "":
                            tooltips[tooltip_id] = tooltips[tooltip_id]\
                                .replace("{" + key + "}", card_names[crd])
                            # We've dealt with this key, move on.
                            continue
                    if variable.attrib['key'] == key:
                        # The value is sometimes given immediately here.
                        if data.attrib['V'] != "":
                            tooltips[tooltip_id] = tooltips[tooltip_id]\
                                .replace("{" + key + "}", data.attrib['V'])
                        else: # Otherwise we are going to have to look in the ability data to find the value.
                            ability_id = variable.find(key).attrib['abilityId']
                            param_name = variable.find(key).attrib['paramName']
                            ability_value = GwentDataHelper._get_card_ability_value(card_abilities, ability_id, param_name)
                            if ability_value is not None:
                                tooltips[tooltip_id] = tooltips[tooltip_id]\
                                    .replace("{" + key + "}", ability_value)

        return tooltips

    @staticmethod
    def _get_card_ability_value(card_abilities, ability_id, param_name):
        ability = card_abilities.get(ability_id)
        if ability is None:
            return None
        if ability.find(param_name) is not None:
            return ability.find(param_name).attrib['V']

    @staticmethod
    def _get_keywords(tooltips):
        keywords_by_tooltip_id = {}
        for tooltip_id in tooltips:
            tooltip = tooltips[tooltip_id]
            keywords = []
            # Find all keywords in info string. E.g. find 'spawn' in '<keyword=spawn>'
            # Can just use en-US here. It doesn't matter, all regions will return the same result.
            result = re.findall(r'<keyword=([^>]+)>', tooltip)
            for key in result:
                keywords.append(key)

            keywords_by_tooltip_id[tooltip_id] = keywords
        return keywords_by_tooltip_id

    def get_tooltips_file(self, locale):
        path = self._folder + "tooltips_" + locale + ".csv"
        if not os.path.isfile(path):
            print("Couldn't find " + locale + " tooltips at " + path)
            exit()
        return path

    def get_card_tooltips(self, locale):
        tooltips_file = open(self.get_tooltips_file(locale), "r")
        tooltips = {}
        for tooltip in tooltips_file:
            split = tooltip.split("\";\"")
            if len(split) < 2 or "tooltip" not in split[1]:
                continue
            tooltip_id = split[1].replace("tooltip_", "").replace("_description", "").replace("\"", "").lstrip("0")

            # Remove any quotation marks and new lines.
            tooltips[tooltip_id] = split[2].replace("\"\n", "").replace("\\n", "\n")

        tooltips_file.close()
        return tooltips

    def get_keyword_tooltips(self, locale):
        tooltips_file = open(self.get_tooltips_file(locale), "r")
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
        path = self._folder + "cards_" + locale + ".csv"
        if not os.path.isfile(path):
            print("Couldn't find " + locale + " card file at " + path)
            exit()

        return path
