#!/usr/bin/python3
import GwentUtils


def create_keyword_json(gwent_data_helper):
    keywords = {}
    for locale in GwentUtils.LOCALES:
        keywordsByLocale = gwent_data_helper.get_keyword_tooltips(locale)
        for keyword_id in keywordsByLocale:
            tooltip = keywordsByLocale[keyword_id]
            if keywords.get(keyword_id) is None:
                keywords[keyword_id] = {}

            keywords[keyword_id][locale] = {}
            keywords[keyword_id][locale]['raw'] = tooltip
            keywords[keyword_id][locale]['text'] = GwentUtils.clean_html(tooltip)
    return keywords
