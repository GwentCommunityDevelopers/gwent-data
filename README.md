# Gwent Data
This project contains scripts that transforms the Gwent card data contained in xml files into a [standardised JSON format](standard-format.json).

### Getting Card Data from game files
* Find and unzip "Path\to\Gwent\GWENT_Data\StreamingAssets\AssetBundles\data\data_definitions".

### Extracting card data from data_definitions.zip
1. Extract the following files:
    * "Templates.xml"
    * "Abilities.xml"
    * "en_us.csv" (Repeat for all locales)
2. Run gwent.py, passing in a folder that contains all the files from step 1 with the desired version.
    e.g. ./gwent.py ../raw/ v0.9.10

## Card Data Notes

### Tooltips
Tooltips contain some HTML tags to flag the keywords. They look something like this:
```
"tooltip": {
  "en-US": "Whenever this unit enters the graveyard, <keyword=resurrect>Resurrect</keyword> it and <keyword=weaken>Weaken</keyword> it by half.",
  ...
},
```

If you want to remove these tags and just have the text, you can use this regex:
`<.*?>`

Here is an example in python for removing the HTML tags:
```
def clean_html(tooltip):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', tooltip)
    return cleantext
```

### Related Cards
The `related` field contains the ids of any token cards. It may be expanded in the future to include other related cards.

## Contributing
Please branch off of master and then submit a PR with your changes. This allows it to be reviewed by other contributors.
