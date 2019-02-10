# Gwent Data
This project contains scripts that transforms the Gwent card data contained in xml files into a nice json format that you can use in your Gwent projects.

## Usage
1. Find and unzip "Path\to\Gwent\GWENT_Data\StreamingAssets\data_definitions". It's a zip file, even if your OS doesn't recognise it as such.
2. Unzip data_definitions.zip e.g. `unzip data_definitions.zip`
3. `gwent-data` uses the Gwent patch version name to generate urls for the card images. Therefore, if you are not supplying your own image url, you'll need to get the latest patch name. Open GOG to find the name of the latest Gwent version e.g. `v1.2.1`
4. Run gwent.py, passing in the data_definitions directory and the patch version name.
    e.g. `python3 gwent.py data_definitions/ -p v1.2.1`
5. Make sure your project conforms the [Gwent Fan Content Guidelines](https://www.playgwent.com/en/fan-content).

### (Optional) Using your own card images
When a Gwent update is released, CDPR sends me a zip file with the new card images. I then run a script to upload them to a Google Cloud Storage bucket so they can be used in `gwent-data`. It usually takes a couple of days after the update for CDPR to send me the images and for me to upload them. Sometimes I am away when an update is released and I am unable to upload card images immediately for an extended period of time. Therefore you may want to host your own card images. CDPR will supply them to you if you message Burza with some details on your Gwent project.

You can use the `-i` or `--images` option to specify your own image url. If you pass in a url with placeholder strings, `gwent-data` will replace them with the correct values.

E.g.

```
python3 gwent.py data_definitions/ -i www.example.com/{cardId}.png
```

This will correctly replace `{cardId}` with the correct value for each card.

Here are all the placeholders you can use:
| Placeholder     | Replaced By                         | Notes                                                                                                                                                                                      |
|-----------------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `{patch}`       | The Gwent patch version name        | If you use this in your image url, you must also supply a patch name using the `-p` argument.  E.g. `python3 gwent.py data_definitions/ -i www.example.com/{patch}/{cardId}.png -p v1.2.1` |
| `{cardId}`      | The card's ingame id                |                                                                                                                                                                                            |
| `{variationId}` | The id of the variation of the card | Variations are an artifact of the old way Gwent stored card data. Currently all cards have 1 variation.                                                                                    |
| `{size}`        | The size of the image               | Possible values: `original`, `high`, `medium`, `low`, `thumbnail`                                                                                                                          |
| `{artId}`       | The id of this card image           | Each card image has an art id that is different to the card id. In the future, cards may have more than 1 card art.                                                                                                                           |

## Contributing
Please branch off of master and then submit a PR with your changes. This allows it to be reviewed by other contributors.
