#!/usr/bin/python3
import GwentUtils

def createKeywordJson(gwentDataHelper):
    keywords = {}
    for locale in GwentUtils.LOCALES:
        keywords[locale] = gwentDataHelper.getKeywordTooltips(locale)

    return keywords
