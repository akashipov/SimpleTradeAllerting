import json
import os
import pathlib


def load_config():
    with open(
        os.path.join(
            pathlib.Path(__file__).parent.resolve(), "files", "config.json"
        ),
        "r",
    ) as f:
        config = json.load(f)
    return config
