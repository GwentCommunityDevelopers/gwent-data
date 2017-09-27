#!/usr/bin/python3
import GwentUtils

class KeywordData:
    def __init__(self, gwentDataHelper):
        self._helper = gwentDataHelper

    def createKeywordJson(self):
        keywords = {}
        for locale in GwentUtils.LOCALES:
            keywords[locale] = self._helper.getKeywordTooltips(locale)

        return keywords
