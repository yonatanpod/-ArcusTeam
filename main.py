import json
from cisco_product_validator import CiscoProductValidator
import os

validator = CiscoProductValidator()
models_list = []

for json_name in os.listdir("jsons"):

    with open('jsons' + os.path.sep + json_name, 'r') as f:
        data = json.load(f)

    # Check if a model already exists in the DB
    if data['model'] in models_list:
        print(f'----File name: {json_name}\n------Model{data["model"]} already exists in DB.')
        continue

    # Validate JSON
    validation_results = validator.validate(data)

    # Adding a model to the DB only if it passed validations
    if not validation_results:
        models_list.append(data['model'])

    print(f'++++File name: {json_name} \n++++++Result: {"Success" if not validation_results else validation_results}')
