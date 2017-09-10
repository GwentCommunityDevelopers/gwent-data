#!/usr/bin/python3
import json
import re

LOCALES = ["en-US", "de-DE", "es-ES", "es-MX", "fr-FR", "it-IT", "ja-JP", "pl-PL", "pt-BR", "ru-RU", "zh-CN", "zh-TW"]

def saveJson(filepath, data):
    print("Saved JSON to: %s" % filepath)
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, sort_keys=True, indent=2, separators=(',', ': '))

def cleanHtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext
