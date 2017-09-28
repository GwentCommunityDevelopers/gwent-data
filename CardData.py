#!/usr/bin/python3
import re
import GwentUtils

IMAGE_SIZES = ['original', 'high', 'medium', 'low', 'thumbnail']

CRAFT_VALUES = {}
CRAFT_VALUES['Common'] = {"standard": 30, "premium": 200, "upgrade": 100}
CRAFT_VALUES['Rare'] = {"standard": 80, "premium": 400, "upgrade": 200}
CRAFT_VALUES['Epic'] = {"standard": 200, "premium": 800, "upgrade": 300}
CRAFT_VALUES['Legendary'] = {"standard": 800, "premium": 1600, "upgrade": 400}

MILL_VALUES = {}
MILL_VALUES['Common'] = {"standard": 10, "premium": 10, "upgrade": 20}
MILL_VALUES['Rare'] = {"standard": 20, "premium": 20, "upgrade": 50}
MILL_VALUES['Epic'] = {"standard": 50, "premium": 50, "upgrade": 80}
MILL_VALUES['Legendary'] = {"standard": 200, "premium": 200, "upgrade": 120}

CATEGORIES = {
    "Aedirn": "Aedirn",
    "Alchemy": "Alchemy",
    "Ambush": "Ambush",
    "An_Craite": "An Craite",
    "Banish_In_Graveyard": "Doomed",
    "Bear": "Bear",
    "Beast": "Beast",
    "Blitz": "Blitz",
    "Blue_Stripes": "Blue Stripes",
    "Breedable": "Breedable",
    "Brokvar": "Brokvar",
    "Cintra": "Cintra",
    "Construct": "Construct",
    "Cursed_One": "Cursed",
    "Devourer": "Devourer",
    "Dimun": "Dimun",
    "Double_Agent": "Double Agent",
    "Draconid": "Draconid",
    "Dragon": "Dragon",
    "Drummond": "Drummond",
    "Dwarf": "Dwarf",
    "Dyrad": "Dryad",
    "Elf": "Elf",
    "Harpy": "Harpy",
    "Heymaey": "Haymaey",
    "Insectoid": "Insectoid",
    "Kaedwen": "Kaedwen",
    "Leader": "Leader",
    "Mage": "Mage",
    "Medic": "Medic",
    "Necrophage": "Necrophage",
    "Non_Decoyable": "Stubborn",
    "Non_Medicable": "Permadeath",
    "Officer": "Officer",
    "Ogroid": "Ogroid",
    "Organic": "Organic",
    "Potion": "Potion",
    "Redania": "Redania",
    "Regressing": "Regressing",
    "Relict": "Relict",
    "Shapeshifter": "Shapeshifter",
    "Soldier": "Soldier",
    "Special": "Special",
    "Specter": "Specter",
    "Spell": "Spell",
    "Spy": "Agent",
    "Support": "Support",
    "Svalblod": "Svalblod",
    "Tactic": "Tactic",
    "Temeria": "Temeria",
    "Tordarroch": "Tordarroch",
    "Tuirseach": "Tuirseach",
    "Vampire": "Vampire",
    "Vodyanoi": "Vodyanoi",
    "War_Machine": "Machine",
    "Weather": "Weather",
    "Wild_Hunt": "Wild Hunt",
    "Witcher": "Witcher"
}


class CardData:
    def __init__(self, gwent_data_helper):
        self.patch = None
        self.imageUrl = None
        self.cardTemplates = gwent_data_helper.get_card_templates()
        self.tooltipData = gwent_data_helper.get_tooltip_data()
        self.abilityData = gwent_data_helper.get_card_abilities()
        self.cardNames = {}
        self.tooltips = {}
        self.flavorStrings = {}

        for locale in GwentUtils.LOCALES:
            self.cardNames[locale] = gwent_data_helper.get_card_names(locale)
            self.tooltips[locale] = gwent_data_helper.get_card_tooltips(locale)
            self.flavorStrings[locale] = gwent_data_helper.get_flavor_strings(locale)

    def create_card_json(self, patch):
        self.patch = patch
        # Replace with these values {0} : card id, {1} : variation id, {0} : image size
        self.imageUrl = "https://firebasestorage.googleapis.com/v0/b/gwent-9e62a.appspot.com/o/images%2F" +\
                        patch + "%2F{0}%2F{1}%2F{2}.png?alt=media"

        card_data = self._create_base_card_json()

        # Requires information about other cards, so needs to be done after we have looked at every card.
        self._evaluate_info_data(card_data)
        # We have to do this as well to catch cards like Botchling, that are explicitly named in the Baron's tooltip.
        self._evaluate_tokens(card_data)
        # After the info text has been evaluated, we can extract the keywords (e.g. deploy).
        self._evaluate_keywords(card_data)
        self._remove_invalid_images(card_data)
        self._remove_unreleased_cards(card_data)

        return card_data

    def _create_base_card_json(self):
        cards = {}

        for template_id in self.cardTemplates:
            template = self.cardTemplates[template_id]
            card = {}
            card['ingameId'] = template.attrib['id']
            card['strength'] = int(template.attrib['power'])
            card['type'] = template.attrib['group']
            card['faction'] = template.attrib['factionId'].replace("NorthernKingdom", "Northern Realms")

            key = template.attrib['dbgStr'].lower().replace(" ", "_").replace("'", "")
            # Remove any underscores from the end.
            if key[-1] == "_":
                key = key[:-1]

            card['name'] = {}
            card['flavor'] = {}
            for region in GwentUtils.LOCALES:
                card['name'][region] = self.cardNames.get(region).get(key)
                card['flavor'][region] = self.flavorStrings.get(region).get(key)

            # False by default, will be set to true if collectible or is a token of a released card.
            card['released'] = False

            if template.find('Tooltip') is not None:
                card['info'] = {}
                card['infoRaw'] = {}
                for region in GwentUtils.LOCALES:
                    # Set to tooltipId for now, we will evaluate after we have looked at every card.
                    card['info'][region] = template.find('Tooltip').attrib['key']

            card['positions'] = []
            card['loyalties'] = []
            for flag in template.iter('flag'):
                key = flag.attrib['name']

                if key == "Loyal" or key == "Disloyal":
                    card['loyalties'].append(key)

                if key == "Melee" or key == "Ranged" or key == "Siege" or key == "Event":
                    card['positions'].append(key)

            card['categories'] = []
            for flag in template.iter('Category'):
                key = flag.attrib['id']
                if key in CATEGORIES:
                    card['categories'].append(CATEGORIES.get(key))

            card['variations'] = {}

            for definition in template.find('CardDefinitions').findall('CardDefinition'):
                variation = {}
                variation_id = definition.attrib['id']

                variation['variationId'] = variation_id
                variation['availability'] = definition.find('Availability').attrib['V']
                collectible = variation['availability'] == "BaseSet"
                variation['collectible'] = collectible

                # If a card is collectible, we know it has been released.
                if collectible:
                    card['released'] = True

                variation['rarity'] = definition.find('Rarity').attrib['V']

                variation['craft'] = CRAFT_VALUES[variation['rarity']]
                variation['mill'] = MILL_VALUES[variation['rarity']]

                art = {}
                for image_size in IMAGE_SIZES:
                    art[image_size] = self.imageUrl.format(card['ingameId'], variation_id, image_size)
                art['artist'] = definition.find("UnityLinks").find("StandardArt").attrib['author']
                variation['art'] = art

                card['variations'][variation_id] = variation

            cards[card['ingameId']] = card

        return cards

    def _evaluate_info_data(self, cards):
        # Now that we have the raw strings, we have to get any values that are missing.
        for card_id in cards:
            for region in GwentUtils.LOCALES:
                # Some cards don't have info.
                if cards[card_id].get('info') is None or cards[card_id]['info'] == "":
                    continue

                # Set info to be the raw tooltip string.
                tooltip_id = cards[card_id]['info'][region]
                cards[card_id]['info'][region] = self.tooltips[region].get(tooltip_id)
                # Regex. Get all strings that lie between a '{' and '}'.
                result = re.findall(r'.*?\{(.*?)\}.*?', cards[card_id]['info'][region])

                tooltip = self.tooltipData.get(tooltip_id)
                for key in result:
                    for variable in tooltip.iter('VariableData'):
                        data = variable.find(key)
                        if data is None:
                            # This is not the right variable for this key, let's check the next one.
                            continue
                        if "crd" in key:
                            # Spawn a specific card.
                            crd = data.attrib['V']
                            if crd != "":
                                cards[card_id]['info'][region] = cards[card_id]['info'][region]\
                                    .replace("{" + key + "}", cards[crd]['name'][region])
                                # We've dealt with this key, move on.
                                continue
                        if variable.attrib['key'] == key:
                            # The value is sometimes given immediately here.
                            if data.attrib['V'] != "":
                                cards[card_id]['info'][region] = cards[card_id]['info'][region]\
                                    .replace("{" + key + "}", data.attrib['V'])
                            else: # Otherwise we are going to have to look in the ability data to find the value.
                                ability_id = variable.find(key).attrib['abilityId']
                                param_name = variable.find(key).attrib['paramName']
                                ability_value = self._get_card_ability_value(ability_id, param_name)
                                if ability_value is not None:
                                    cards[card_id]['info'][region] = cards[card_id]['info'][region]\
                                        .replace("{" + key + "}", ability_value)

                cards[card_id]['infoRaw'][region] = cards[card_id]['info'][region]
                cards[card_id]['info'][region] = GwentUtils.clean_html(cards[card_id]['info'][region])

    @staticmethod
    def _evaluate_keywords(cards):
        for card_id in cards:
            card = cards[card_id]
            if card.get('infoRaw') is None:
                continue
            card['keywords'] = []
            # Find all keywords in info string. E.g. find 'spawn' in '<keyword=spawn>'
            # Can just use en-US here. It doesn't matter, all regions will return the same result.
            result = re.findall(r'<keyword=([^>]+)>', card['infoRaw']['en-US'])
            for key in result:
                card['keywords'].append(key)

    # If a card is not collectible, we don't have the art for it.
    @staticmethod
    def _remove_invalid_images(cards):
        for card_id in cards:
            card = cards[card_id]
            for variation_id in card['variations']:
                variation = card['variations'][variation_id]
                if not variation['collectible']:
                    for size in IMAGE_SIZES:
                        del variation['art'][size]

    @staticmethod
    def _remove_unreleased_cards(cards):
        # A few cards get falsely flagged as released.

        # Gaunter's 'Higher than 5' token
        cards['200175']['released'] = False
        # Gaunter's 'Lower than 5' token
        cards['200176']['released'] = False

    # If a card is a token of a released card, it has also been released.
    def _evaluate_tokens(self, cards):
        for card_id in cards:
            card = cards[card_id]
            if card['released']:
                card['related'] = []
                for ability in self.cardTemplates[card_id].iter('Ability'):
                    ability = self.abilityData.get(ability.attrib['id'])
                    if ability is None:
                        continue

                    # There are several different ways that a template can be referenced.
                    for template in ability.iter('templateId'):
                        token_id = template.attrib['V']
                        token = cards.get(token_id)
                        if self._is_token_valid(token):
                            cards.get(token_id)['released'] = True
                            if token_id not in card['related']:
                                card['related'].append(token_id)

                    for template in ability.iter('TemplatesFromId'):
                        for token in template.iter('id'):
                            token_id = token.attrib['V']
                            token = cards.get(token_id)
                            if self._is_token_valid(token):
                                cards.get(token_id)['released'] = True
                                if token_id not in card['related']:
                                    card['related'].append(token_id)

                    for template in ability.iter('TransformTemplate'):
                        token_id = template.attrib['V']
                        token = cards.get(token_id)
                        if self._is_token_valid(token):
                            cards.get(token_id)['released'] = True
                            if token_id not in card['related']:
                                card['related'].append(token_id)

                    for template in ability.iter('TemplateId'):
                        token_id = template.attrib['V']
                        token = cards.get(token_id)
                        if self._is_token_valid(token):
                            token['released'] = True
                            if token_id not in card['related']:
                                card['related'].append(token_id)

                # We may not have added any cards to 'related'.
                if len(card['related']) == 0:
                    del card['related']

    @staticmethod
    def _is_token_valid(token):
        if token is not None and token.get('info') is not None:
            valid = True
            for region in token['info']:
                if token['info'].get(region) is None or token['info'][region] == '':
                    valid = False
            return valid
        else:
            return False

    def _get_card_ability_value(self, ability_id, param_name):
        ability = self.abilityData.get(ability_id)
        if ability is None:
            return None
        if ability.find(param_name) is not None:
            return ability.find(param_name).attrib['V']
