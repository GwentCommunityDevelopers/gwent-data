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

"""
Gwent Card Sets
"""
TOKEN_SET = 0
BASE_SET = 1
TUTORIAL_SET = 2
THRONEBREAKER_SET = 3
UNMILLABLE_SET = 10

CARD_SETS = {
    TOKEN_SET: "NonOwnable",
    BASE_SET: "BaseSet",
    TUTORIAL_SET: "Tutorial",
    THRONEBREAKER_SET: "Thronebreaker",
    UNMILLABLE_SET: "Unmillable"
}

# Gaunter's 'Higher than 5' and 'Lower than 5' are not actually cards.
INVALID_TOKENS = ['200175', '200176']

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
        tier = int(template.find('Tier').text)
        card['type'] = TYPES.get(tier)
        card['faction'] = FACTIONS.get(int(template.find('FactionId').text))
        card['provision'] = int(template.find('Provision').text)
        if (tier == LEADER):
            card['mulligans'] = int(template.find('Mulligans').text)

        maxRange = int(template.find('MaxRange').text)
        if (maxRange > -1):
            card['reach'] = maxRange

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

        # There are 2 category nodes
        for node in ["PrimaryCategory", "Categories"]:
            for multiplier in range(2):
                # e0, e1
                e = "e{0}".format(multiplier)
                categories_sum = int(template.find(node).find(e).attrib['V'])
                for category, bit in enumerate("{0:b}".format(categories_sum)[::-1]):
                    if bit == '1':
                        # e1 categories are off by 64.
                        adjusted_category = category + (64 * multiplier)
                        card['categoryIds'].append("card_category_{0}".format(adjusted_category))

        categories_en_us = gwent_data_helper.categories["en-US"]
        for category_id in card['categoryIds']:
            if category_id in categories_en_us:
                card['categories'].append(categories_en_us[category_id])

        # Variations no longer exist in Gwent. To maintain backwards compatability, create 1 variation.
        card['variations'] = {}
        variation = {}
        variation_id = card_id + "00" # Old variation id format.

        availability = int(template.attrib['Availability'])

        variation['variationId'] = variation_id

        variation['availability'] = CARD_SETS[availability]
        collectible = availability == BASE_SET or availability == THRONEBREAKER_SET or availability == UNMILLABLE_SET
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

        art_id = template.attrib.get('ArtId')
        if art_id != None:
            art['ingameArtId'] = art_id

        variation['art'] = art

        card['variations'][variation_id] = variation
        artist = gwent_data_helper.artists.get(art_id)
        if artist != None:
            card['artist'] = artist

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

    # Remove any unreleased cards
    for card_id, card in list(cards.items()):
        if not card['released']:
            del cards[card_id]

    return cards
