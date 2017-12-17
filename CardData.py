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
            card['name'][region] = gwent_data_helper.card_names.get(region).get(key)
            card['flavor'][region] = gwent_data_helper.flavor_strings.get(region).get(key)

        # False by default, will be set to true if collectible or is a token of a released card.
        card['released'] = False

        if template.find('Tooltip') is not None:
            tooltip_id = template.find('Tooltip').attrib['key']
            card['info'] = {}
            card['infoRaw'] = {}
            for locale in GwentUtils.LOCALES:
                tooltip = gwent_data_helper.tooltips[locale].get(tooltip_id)
                if tooltip is not None:
                    card['infoRaw'][locale] = tooltip
                    card['info'][locale] = GwentUtils.clean_html(tooltip)

            card['keywords'] = gwent_data_helper.keywords.get(tooltip_id)

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
            if collectible:
                for image_size in IMAGE_SIZES:
                    art[image_size] = imageUrl.format(card['ingameId'], variation_id, image_size)
            art['artist'] = definition.find("UnityLinks").find("StandardArt").attrib['author']
            variation['art'] = art

            card['variations'][variation_id] = variation

        tokens = gwent_data_helper.tokens.get(card['ingameId'])
        card['related'] = tokens

        cards[card['ingameId']] = card

    # Check tokens are correctly marked as released.
    for card_id in cards:
        card = cards[card_id]
        if card['released'] and card.get('related') is not None:
            for token_id in card.get('related'):
                cards[token_id]['released'] = token_id not in INVALID_TOKENS

    return cards
