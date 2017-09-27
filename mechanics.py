#!/usr/bin/python3
import GwentUtils

class KeywordData:
    def __init__(self, gwentData):
        self._gwentData = gwentData

    def getKeywords(self, locale):
        keywords = {}

        for tooltip in self._gwentData.tooltips:
            split = tooltip.split("\";\"")
            if len(split) < 2 or "keyword" not in split[1]:
                continue
            keywordId = split[1].replace("keyword_","").replace("\"", "")

            keywords[keywordId] = {}
            # Remove any quotation marks and new lines.
            keywords[keywordId]['raw'] = split[2].replace("\"", "").replace("\n", "")
            keywords[keywordId]['unformatted'] = utils.cleanHtml(keywords[keywordId]['raw'])

        return keywords

def createKeywordJson(gwentData):
    keywordData = KeywordData(gwentData)
    keywords = {}
    for locale in GwentUtils.LOCALES:
        localisedKeywords = keywordData.getKeywords(locale)
        keywords[locale] = localisedKeywords

    return keywords
