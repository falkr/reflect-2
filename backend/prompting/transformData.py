import json
import os
from typing import List, Dict, Any

absolute_path = os.path.dirname(__file__)


# Transformation script
def transform_data(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, "r") as file:
        # Last inn hele JSON-filen
        full_data = json.load(file)

    # Bruker 'data'-nøkkelen for å få listen med elementer
    data = full_data["data"]

    transformed = []
    for item in data:
        transformed_item = {
            "learning_unit": item["learning_unit"],
            "participation": item["participation"],
            "answers": [
                item["best_learning_success"],
                item["least_understood_concept"],
            ],
            "key": item["key"],
        }
        transformed.append(transformed_item)

    # Lagre den transformerte dataen til en ny fil
    output_file_path = os.path.join(absolute_path, "data/new.json")
    with open(output_file_path, "w") as file:
        json.dump(transformed, file, indent=2)

    return transformed


# Angi riktig filbane til 'output.json'
file_path = os.path.join(absolute_path, "data/inputToPostman.json")
transform_data(file_path)
