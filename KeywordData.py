#!/usr/bin/python3
import GwentUtils


class KeywordData:
    def __init__(self, gwent_data_helper):
        self._helper = gwent_data_helper

    def create_keyword_json(self):
        keywords = {}
        for locale in GwentUtils.LOCALES:
            keywords[locale] = self._helper.get_keyword_tooltips(locale)

        return keywords
