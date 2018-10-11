# Gwent Data
This project contains scripts that transforms the Gwent card data contained in xml files into a [standardised JSON format](standard-format.json).

### Getting Card Data from game files
* Find and unzip "Path\to\Gwent\GWENT_Data\StreamingAssets\AssetBundles\data\data_definitions".

### Extracting card data from data_definitions.zip
1. Unzip data_definitions.zip
2. Run gwent.py, passing in a folder that contains all the files from step 1 with the desired version. (Version is used to generate card image urls)
    e.g. ./gwent.py data_definitions/ v0.9.10

## Contributing
Please branch off of master and then submit a PR with your changes. This allows it to be reviewed by other contributors.
