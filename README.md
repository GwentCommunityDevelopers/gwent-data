# Gwent Data
This project contains scripts that transform the Gwent card data contained in xml files into a [standardised JSON format](standard-format.json).

### Getting Card Data from game files
* Find and unzip "Path\to\Gwent\GWENT_Data\StreamingAssets\AssetBundles\data\data_definitions".

### Extracting card data from data_definitions.zip
1. Extract the following files:
    * "GwentCardTemplates.xml"
    * "GwentCardAbilities.xml",
    * "GwentTooltips.xml",
    * "cards_en-US" (Repeat for all locales. Rename them so that they are in the format 'xx-XX'. Upper case is important)
    * "tooltips_en-US". (Repeat for all locales. Rename them so that they are in the format 'xx-XX'. Upper case is important)
2. In GwentCardTemplates.xml, Find and replace "&" with "&amp;" (ignoring quotes). & is invalid xml.
3. In GwentCardAbilities.xml, Find and replace "{dmg}" with "dmg" (ignoring quotes).
4. Run master_xml.py, passing in a folder that contains all the files from step 1.
    e.g. ./master_xml.py ../raw/
