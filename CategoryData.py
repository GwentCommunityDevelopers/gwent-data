#!/usr/bin/python3
import GwentUtils

def create_category_json(gwent_data_helper):
    categories = {}
    for locale in GwentUtils.LOCALES:
        categoriesByLocale = gwent_data_helper.categories[locale]
        for category_id in categoriesByLocale:
            text = categoriesByLocale[category_id]
            if categories.get(category_id) is None:
                categories[category_id] = {}

            categories[category_id][locale] = text
    return categories
