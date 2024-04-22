from metadata import Metadata
import json

metadata = Metadata.get_metadata_without_zenodo()
with open('hardware_info.json', "w") as fp:
    json.dump(metadata, fp, indent=4)
