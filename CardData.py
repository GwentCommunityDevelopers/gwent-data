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
    def __init__(self, gwentDataHelper):
        self._helper = gwentDataHelper
        self.cardTemplates = self._helper.getCardTemplates()
        self.tooltipData = self._helper.getTooltipData()
        self.abilityData = self._helper.getCardAbilities()
        self.cardNames = {}
        self.tooltips = {}
        self.flavorStrings = {}

        for locale in GwentUtils.LOCALES:
            self.cardNames[locale] = self._helper.getCardNames(locale)
            self.tooltips[locale] = self._helper.getCardTooltips(locale)
            self.flavorStrings[locale] = self._helper.getFlavorStrings(locale)

    def createCardJson(self, patch):
        self.patch = patch
        # Replace with these values {0} : card id, {1} : variation id, {0} : image size
        self.imageUrl = "https://firebasestorage.googleapis.com/v0/b/gwent-9e62a.appspot.com/o/images%2F" + patch + "%2F{0}%2F{1}%2F{2}.png?alt=media"

        cardData = self._createBaseCardJson()

        # Requires information about other cards, so needs to be done after we have looked at every card.
        self._evaluateInfoData(cardData)
        # We have to do this as well to catch cards like Botchling, that are explicitly named in the Baron's tooltip.
        self._evaluateTokens(cardData)
        # After the info text has been evaluated, we can extract the keywords (e.g. deploy).
        self._evaluateKeywords(cardData)
        self._removeInvalidImages(cardData)
        self._removeUnreleasedCards(cardData)

        return cardData

    def _createBaseCardJson(self):
        cards = {}

        for templateId in self.cardTemplates:
            template = self.cardTemplates[templateId]
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

            if (template.find('Tooltip') != None):
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
                variationId = definition.attrib['id']

                variation['variationId'] = variationId
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
                for imageSize in IMAGE_SIZES:
                    art[imageSize] = self.imageUrl.format(card['ingameId'], variationId, imageSize)
                art['artist'] = definition.find("UnityLinks").find("StandardArt").attrib['author']
                variation['art'] = art

                card['variations'][variationId] = variation

            cards[card['ingameId']] = card

        return cards

    def _evaluateInfoData(self, cards):
        # Now that we have the raw strings, we have to get any values that are missing.
        for cardId in cards:
            defaultEvaluated = False
            for region in GwentUtils.LOCALES:
                # Some cards don't have info.
                if cards[cardId].get('info') == None or cards[cardId]['info'] == "":
                    continue

                # Set info to be the raw tooltip string.
                tooltipId = cards[cardId]['info'][region]
                cards[cardId]['info'][region] = self.tooltips[region].get(tooltipId)
                result = re.findall(r'.*?\{(.*?)\}.*?', cards[cardId]['info'][region]) # Regex. Get all strings that lie between a '{' and '}'.

                tooltip = self.tooltipData.get(tooltipId)
                for key in result:
                    for variable in tooltip.iter('VariableData'):
                        data = variable.find(key)
                        if data == None:
                            # This is not the right variable for this key, let's check the next one.
                            continue
                        if "crd" in key:
                            # Spawn a specific card.
                            crd = data.attrib['V']
                            if crd != "":
                                cards[cardId]['info'][region] = cards[cardId]['info'][region].replace("{" + key + "}", cards[crd]['name'][region])
                                # We've dealt with this key, move on.
                                continue
                        if variable.attrib['key'] == key:
                            # The value is sometimes given immediately here.
                            if data.attrib['V'] != "":
                                cards[cardId]['info'][region] = cards[cardId]['info'][region].replace("{" + key + "}", data.attrib['V'])
                            else: # Otherwise we are going to have to look in the ability data to find the value.
                                abilityId = variable.find(key).attrib['abilityId']
                                paramName = variable.find(key).attrib['paramName']
                                abilityValue = self._getCardAbilityValue(abilityId, paramName)
                                if abilityValue != None:
                                    cards[cardId]['info'][region] = cards[cardId]['info'][region].replace("{" + key + "}", abilityValue)

                cards[cardId]['infoRaw'][region] = cards[cardId]['info'][region]
                cards[cardId]['info'][region] = GwentUtils.cleanHtml(cards[cardId]['info'][region])

    def _evaluateKeywords(self, cards):
        for cardId in cards:
            card = cards[cardId]
            if card.get('infoRaw') == None:
                continue
            card['keywords'] = []
            # Find all keywords in info string. E.g. find 'spawn' in '<keyword=spawn>'
            # Can just use en-US here. It doesn't matter, all regions will return the same result.
            result = re.findall(r'<keyword=([^>]+)>', card['infoRaw']['en-US'])
            for key in result:
                card['keywords'].append(key)

    # If a card is not collectible, we don't have the art for it.
    def _removeInvalidImages(self, cards):
        for cardId in cards:
            card = cards[cardId]
            for variationId in card['variations']:
                variation = card['variations'][variationId]
                if not variation['collectible']:
                    for size in IMAGE_SIZES:
                        del variation['art'][size]

    def _removeUnreleasedCards(self, cards):
        # A few cards get falsely flagged as released.

        # Gaunter's 'Higher than 5' token
        cards['200175']['released'] = False
        # Gaunter's 'Lower than 5' token
        cards['200176']['released'] = False

    # If a card is a token of a released card, it has also been released.
    def _evaluateTokens(self, cards):
        for cardId in cards:
            card = cards[cardId]
            if card['released']:
                card['related'] = []
                for ability in self.cardTemplates[cardId].iter('Ability'):
                    ability = self.abilityData.get(ability.attrib['id'])
                    if ability == None:
                        continue

                    # There are several different ways that a template can be referenced.
                    for template in ability.iter('templateId'):
                        tokenId = template.attrib['V']
                        token = cards.get(tokenId)
                        if self._isTokenValid(token):
                            cards.get(tokenId)['released'] = True
                            if tokenId not in card['related']:
                                card['related'].append(tokenId)

                    for template in ability.iter('TemplatesFromId'):
                        for token in template.iter('id'):
                            tokenId = token.attrib['V']
                            token = cards.get(tokenId)
                            if self._isTokenValid(token):
                                cards.get(tokenId)['released'] = True
                                if tokenId not in card['related']:
                                    card['related'].append(tokenId)

                    for template in ability.iter('TransformTemplate'):
                        tokenId = template.attrib['V']
                        token = cards.get(tokenId)
                        if self._isTokenValid(token):
                            cards.get(tokenId)['released'] = True
                            if tokenId not in card['related']:
                                card['related'].append(tokenId)

                    for template in ability.iter('TemplateId'):
                        tokenId = template.attrib['V']
                        token = cards.get(tokenId)
                        if self._isTokenValid(token):
                            token['released'] = True
                            if tokenId not in card['related']:
                                card['related'].append(tokenId)

    def _isTokenValid(self, token):
        if token != None and token.get('info') != None:
            valid = True
            for region in token['info']:
                if token['info'].get(region) == None or token['info'][region] == '':
                    valid = False
            return valid
        else:
            return False

    def _getCardAbilityValue(self, abilityId, paramName):
        ability = self.abilityData.get(abilityId)
        if ability == None:
            return None
        if ability.find(paramName) != None:
            return ability.find(paramName).attrib['V']
