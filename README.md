# Gwent Data
This project contains scripts that transforms the Gwent card data contained in xml files into a [standardised JSON format](standard-format.json).

### Getting Card Data from game files
* Find and unzip "Path\to\Gwent\GWENT_Data\StreamingAssets\AssetBundles\data\data_definitions".

### Extracting card data from data_definitions.zip
1. Extract the following files:
    * "GwentCardTemplates.xml"
    * "GwentCardAbilities.xml"
    * "GwentTooltips.xml"
    * "cards_en-US.xml" (Repeat for all locales. Rename them so that they are in the format 'xx-XX'. Upper case is important)
    * "tooltips_en-US.xml" (Repeat for all locales. Rename them so that they are in the format 'xx-XX'. Upper case is important)
2. Rename "cards_jp-JP.xml" and "tooltips_jp-JP.xml" to "cards_ja-JP.xml" and "tooltips_ja-JP.xml" respectively.
3. In GwentCardTemplates.xml, Find and replace ``&`` with ``&amp;``. ``&`` is invalid xml.
4. In GwentTooltips.xml, Find and replace ``{dmg}`` with ``dmg``. ``{`` and ``}`` are invalid xml.
5. Run master_xml.py, passing in a folder that contains all the files from step 1 with the desired version.
    e.g. ./master_xml.py ../raw/ v0.9.10

## Contributing
Please branch off of master and then submit a PR with your changes. This allows it to be reviewed by other contributors.
