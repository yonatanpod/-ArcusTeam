import json
from cisco_product_validator import CiscoProductValidator
import os

validator = CiscoProductValidator()
models_list = []

for json_name in os.listdir("jsons"):

    with open('jsons' + os.path.sep + json_name, 'r') as f:
        data = json.load(f)

    if data['model'] in models_list:
        print(f'----File name: {json_name}\n------Model{data["model"]} already exists in DB.')
        continue

    models_list.append(data['model'])
    validation_results = validator.validate(data)

    print(f'++++File name: {json_name} \n++++++Result: {"Success" if not validation_results else validation_results}')
