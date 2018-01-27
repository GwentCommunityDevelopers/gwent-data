#!/usr/bin/python3
import re
import GwentUtils

IMAGE_SIZES = ['original', 'high', 'medium', 'low', 'thumbnail']

"""
Constants from Gwent Client.
"""
COMMON = 1
RARE = 2
EPIC = 4
LEGENDARY = 8

LEADER = 1
BRONZE = 2
SILVER = 4
GOLD = 8

NEUTRAL = 1
MONSTER = 2
NILFGAARD = 4
NORTHERN_REALMS = 8
SCOIATAEL = 16
SKELLIGE = 32

"""
Mill and Crafting values for each rarity.
"""
CRAFT_VALUES = {}
CRAFT_VALUES[COMMON] = {"standard": 30, "premium": 200, "upgrade": 100}
CRAFT_VALUES[RARE] = {"standard": 80, "premium": 400, "upgrade": 200}
CRAFT_VALUES[EPIC] = {"standard": 200, "premium": 800, "upgrade": 300}
CRAFT_VALUES[LEGENDARY] = {"standard": 800, "premium": 1600, "upgrade": 400}

MILL_VALUES = {}
MILL_VALUES[COMMON] = {"standard": 10, "premium": 10, "upgrade": 20}
MILL_VALUES[RARE] = {"standard": 20, "premium": 20, "upgrade": 50}
MILL_VALUES[EPIC] = {"standard": 50, "premium": 50, "upgrade": 80}
MILL_VALUES[LEGENDARY] = {"standard": 200, "premium": 200, "upgrade": 120}

"""
Gwent Client ID -> Gwent Data ID mapping.
"""
RARITIES = { COMMON: "Common", RARE: "Rare", EPIC: "Epic", LEGENDARY: "Legendary"}
TYPES = { LEADER: "Leader", BRONZE: "Bronze", SILVER: "Silver", GOLD: "Gold"}
FACTIONS = { NEUTRAL: "Neutral", MONSTER: "Monster", NILFGAARD: "Nilfgaard",
    NORTHERN_REALMS: "Northern Realms", SCOIATAEL: "Scoiatael", SKELLIGE: "Skellige"}

# Gaunter's 'Higher than 5' and 'Lower than 5' are not actually cards.
INVALID_TOKENS = ['200175', '200176']

"""
 Categories are stored as sums of powers of 2. Use the ID from here to look up
 localisations in categories output file.
"""
CATEGORIES = {
    2**1: "card_category_1",
    2**10: "card_category_10",
    2**11: "card_category_11",
    2**12: "card_category_12",
    2**13: "card_category_13",
    2**14: "card_category_14",
    2**15: "card_category_15",
    2**16: "card_category_16",
    2**17: "card_category_17",
    2**18: "card_category_18",
    2**19: "card_category_19",
    2**2: "card_category_2",
    2**20: "card_category_20",
    2**21: "card_category_21",
    2**22: "card_category_22",
    2**23: "card_category_23",
    2**24: "card_category_24",
    2**25: "card_category_25",
    2**26: "card_category_26",
    2**27: "card_category_27",
    2**28: "card_category_28",
    2**29: "card_category_29",
    2**3: "card_category_3",
    2**30: "card_category_30",
    2**31: "card_category_31",
    2**32: "card_category_32",
    2**33: "card_category_33",
    2**34: "card_category_34",
    2**35: "card_category_35",
    2**36: "card_category_36",
    2**37: "card_category_37",
    2**38: "card_category_38",
    2**39: "card_category_39",
    2**4: "card_category_4",
    2**40: "card_category_40",
    2**41: "card_category_41",
    2**42: "card_category_42",
    2**43: "card_category_43",
    2**44: "card_category_34",
    2**46: "card_category_46",
    2**47: "card_category_47",
    2**48: "card_category_48",
    2**49: "card_category_49",
    2**5: "card_category_5",
    2**50: "card_category_50",
    2**51: "card_category_51",
    2**52: "card_category_52",
    2**53: "card_category_53",
    2**54: "card_category_54",
    2**55: "card_category_55",
    2**56: "card_category_56",
    2**57: "card_category_57",
    2**58: "card_category_58",
    2**59: "card_category_59",
    2**6: "card_category_6",
    2**60: "card_category_60",
    2**61: "card_category_61",
    2**62: "card_category_62",
    2**63: "card_category_63",
    2**64: "card_category_64",
    2**65: "card_category_65",
    2**66: "card_category_66",
    2**67: "card_category_67",
    2**68: "card_category_68",
    2**69: "card_category_69",
    2**7: "card_category_7",
    2**70: "card_category_70",
    2**71: "card_category_71",
    2**8: "card_category_8",
    2**9: "card_category_9",
    2**73: "card_category_73"
}

def create_card_json(gwent_data_helper, patch):
    # Replace with these values {0} : card id, {1} : variation id, {2} : image size
    imageUrl = "https://firebasestorage.googleapis.com/v0/b/gwent-9e62a.appspot.com/o/images%2F" +\
                    patch + "%2F{0}%2F{1}%2F{2}.png?alt=media"

    cards = {}

    card_templates = gwent_data_helper.card_templates
    for template_id in card_templates:
        template = card_templates[template_id]
        card = {}
        card_id = template.attrib['Id']
        card['ingameId'] = card_id
        card['strength'] = int(template.find('Power').text)
        card['type'] = TYPES.get(int(template.find('Tier').text))
        card['faction'] = FACTIONS.get(int(template.find('FactionId').text))

        card['name'] = {}
        card['flavor'] = {}
        for region in GwentUtils.LOCALES:
            card['name'][region] = gwent_data_helper.card_names.get(region).get(card_id)
            card['flavor'][region] = gwent_data_helper.flavor_strings.get(region).get(card_id)

        # False by default, will be set to true if collectible or is a token of a released card.
        card['released'] = False

        # Tooltips
        card['info'] = {}
        card['infoRaw'] = {}
        for locale in GwentUtils.LOCALES:
            tooltip = gwent_data_helper.tooltips[locale].get(card_id)
            if tooltip is not None:
                card['infoRaw'][locale] = tooltip
                card['info'][locale] = GwentUtils.clean_html(tooltip)

        # Keywords.
        card['keywords'] = gwent_data_helper.keywords.get(card_id)

        # Units no longer have a row restriction.
        card['positions'] = ["Melee", "Ranged", "Siege"]

        # Loyalty
        card['loyalties'] = []
        placement = template.find('Placement')
        if placement.attrib['PlayerSide'] != "0":
            card['loyalties'].append("Loyal")
        if placement.attrib['OpponentSide'] != "0":
            card['loyalties'].append("Disloyal")

        # Categories
        card['categories'] = []
        card['categoryIds'] = []
        categoriesSum = int(template.find('Categories').find('e0').attrib['V']);
        # XML Card category is the sum of all categories of the card
        for category in sorted(CATEGORIES, reverse=True):
            if categoriesSum - category >= 0:
                categoriesSum -= category
                card['categoryIds'].append(CATEGORIES[category])
            if categoriesSum == 0:
                break

        categories_en_us = gwent_data_helper.categories["en-US"]
        for category_id in card['categoryIds']:
            if category_id in categories_en_us:
                card['categories'].append(categories_en_us[category_id])

        # Variations no longer exist in Gwent. To maintain backwards compatability, create 1 variation.
        card['variations'] = {}
        variation = {}
        variation_id = card_id + "00" # Old variation id format.

        availability = int(template.attrib['Availability'])
        if availability == 1:
            variation['availability'] = "BaseSet"
        else:
            variation['availability'] = "NonOwnable"

        variation['variationId'] = variation_id

        collectible = availability == 1
        variation['collectible'] = collectible

        # If a card is collectible, we know it has been released.
        if collectible:
            card['released'] = True

        rarity = int(template.find('Rarity').text)
        variation['rarity'] = RARITIES.get(rarity)

        variation['craft'] = CRAFT_VALUES.get(rarity)
        variation['mill'] = MILL_VALUES.get(rarity)

        art = {}
        if collectible:
            for image_size in IMAGE_SIZES:
                art[image_size] = imageUrl.format(card['ingameId'], variation_id, image_size)
        art_definition = template.find('ArtDefinition')

        if art_definition != None:
            art['ingameArtId'] = art_definition.attrib.get('ArtId')

        variation['art'] = art

        card['variations'][variation_id] = variation

        # Add all token cards to the 'related' list.
        tokens = gwent_data_helper.tokens.get(card['ingameId'])
        card['related'] = tokens

        cards[card_id] = card

    # Check tokens are correctly marked as released.
    for card_id in cards:
        card = cards[card_id]
        if card['released'] and card.get('related') is not None:
            for token_id in card.get('related'):
                if token_id in cards:
                    cards[token_id]['released'] = token_id not in INVALID_TOKENS

    return cards
