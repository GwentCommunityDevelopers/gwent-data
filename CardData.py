#!/usr/bin/python3
import re
import GwentUtils

IMAGE_SIZES = ['original', 'high', 'medium', 'low', 'thumbnail']

CRAFT_VALUES = {}
CRAFT_VALUES[1] = {"standard": 30, "premium": 200, "upgrade": 100}
CRAFT_VALUES[2] = {"standard": 80, "premium": 400, "upgrade": 200}
CRAFT_VALUES[4] = {"standard": 200, "premium": 800, "upgrade": 300}
CRAFT_VALUES[8] = {"standard": 800, "premium": 1600, "upgrade": 400}

MILL_VALUES = {}
MILL_VALUES[1] = {"standard": 10, "premium": 10, "upgrade": 20}
MILL_VALUES[2] = {"standard": 20, "premium": 20, "upgrade": 50}
MILL_VALUES[4] = {"standard": 50, "premium": 50, "upgrade": 80}
MILL_VALUES[8] = {"standard": 200, "premium": 200, "upgrade": 120}

RARITIES = { 1: "Common", 2: "Rare", 4: "Epic", 8: "Legendary"}
TYPES = { 1: "Leader", 2: "Bronze", 4: "Silver", 8: "Gold"}
FACTIONS = { 1: "Neutral", 2: "Monster", 4: "Nilfgaard", 8: "Northern Realms", 16: "Scoiatael", 32: "Skellige"}

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

# Gaunter's 'Higher than 5' and 'Lower than 5' are not actually cards.
INVALID_TOKENS = ['200175', '200176']


def create_card_json(gwent_data_helper, patch):
    # Replace with these values {0} : card id, {1} : variation id, {0} : image size
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

        card['info'] = {}
        card['infoRaw'] = {}
        for locale in GwentUtils.LOCALES:
            tooltip = gwent_data_helper.tooltips[locale].get(card_id)
            if tooltip is not None:
                card['infoRaw'][locale] = tooltip
                card['info'][locale] = GwentUtils.clean_html(tooltip)

        card['keywords'] = gwent_data_helper.keywords.get(card_id)

        card['positions'] = ["Melee", "Ranged", "Siege"]
        card['loyalties'] = []
        placement = template.find('Placement')
        if placement.attrib['PlayerSide'] != "0":
            card['loyalties'].append("Loyal")
        if placement.attrib['OpponentSide'] != "0":
            card['loyalties'].append("Disloyal")

        card['categories'] = []

        card['variations'] = {}
        for x in range(1):
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
            variation['art'] = art

            card['variations'][variation_id] = variation

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
