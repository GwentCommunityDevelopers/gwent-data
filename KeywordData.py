#!/usr/bin/python3
import GwentUtils

def create_keyword_json(gwent_data_helper):
    keywords = {}
    for locale in GwentUtils.LOCALES:
        keywords[locale] = gwent_data_helper.get_keyword_tooltips(locale)

    return keywords
