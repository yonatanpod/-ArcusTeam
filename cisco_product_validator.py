import json
from jsonschema import validate
import re
import requests
import urllib.request
from bs4 import BeautifulSoup


class CiscoProductValidator(object):
    """
    A Validator for the CISCO products' JSON files.
    """
    json_schema = None
    path_regex = None
    url_path_regex = None
    first_cisco_product_release = 504921600  # First CISCO product was released in 1986

    def __init__(self, schema_path: str = "expected schema.json"):
        """
        Initializing variables.
        :param schema_path: path to schema file that describes the JSON schema.
        """
        with open(schema_path, 'r') as f:
            self.json_schema = json.load(f)
        self.path_regex = re.compile(r'^(/)?([^/\0]+(/)?)+$')
        self.url_path_regex = re.compile(r'^((https|ftp|file)?([Cc])?:\/\/)?(www.)?')

    def validate_schema(self, my_json: dict) -> bool:
        """
        Validating that JSON schema matches the expected schema.
        :param my_json: JSON file to check.
        :return: True if schema matched.
        """
        try:
            validate(my_json, self.json_schema)
            return True
        except:
            return False

    def validate_unix_path(self, my_json: dict) -> bool:
        """
        Validating that the path field in the JSON is a UNIX path.
        :param my_json: JSON file to check.
        :return: True if the path is a UNIX path.
        """
        if self.path_regex.match(my_json['path']):
            return True
        else:
            return False

    def validate_product_url(self, my_json: dict) -> bool:
        """
        Validating that the product url is alive.
        :param my_json: JSON file to check.
        :return: True if the url is alive.
        """
        try:
            if requests.get(my_json['url']).status_code == 200:
                return True
            else:
                return False
        except:
            return False

    def validate_download_link(self, my_json: dict) -> bool:
        """
        Validate that download url is a url and is alive.
        :param my_json: JSON file to check.
        :return: True if the link exists and alive.
        """
        for item in my_json['downloads']:
            if 'all' not in item:
                continue
            if not self.url_path_regex.match(item['all']):
                return False
            try:
                return requests.get(item['all']).status_code == 200
            except:
                return False

    def validate_dates(self, my_json: dict) -> bool:
        """
        Validate dates: release date is mandatory, endofsale has to be after release date,
        endofsupport has to be the latest date.
        Endofsale and endofsupport can be missing.
        :param my_json: JSON file to check.
        :return: True if all the dates are consistent.
        """
        if my_json['release'] > self.first_cisco_product_release:
            if my_json['endofsale'] is not None:
                if my_json['endofsupport'] is not None:
                    return my_json['release'] < my_json['endofsale'] < my_json['endofsupport']
                else:
                    return my_json['release'] < my_json['endofsale']
            else:
                if my_json['endofsupport'] is not None:
                    return my_json['release'] < my_json['endofsupport']
                else:
                    return False
        else:
            return False

    def validate_model(self, my_json: dict) -> bool:
        """
        Validate that model field in the JSON is the same as in HTML.
        :param my_json: JSON file to check.
        :return: True if the strings match.
        """
        try:
            page = urllib.request.urlopen(my_json['url'])
            mybytes = page.read()
            the_html = mybytes.decode("utf8")
            page.close()
            soup = BeautifulSoup(the_html, features='lxml')
            if my_json['model'] in soup.h1.get_text():
                return True
            else:
                return False
        except:
            return False

    def validate(self, my_json: dict) -> list:
        """
        Running all the validations and saving errors in a list.
        :param my_json: JSON file to check.
        :return: Empty list if there were no errors, list of errors otherwise.
        """
        failed = []
        if not self.validate_schema(my_json):
            failed.append("Schema is not correct")
        if not self.validate_unix_path(my_json):
            failed.append("Failed to validate UNIX path")
        if not self.validate_product_url(my_json):
            failed.append("Could not connect to the product page")
        if not self.validate_download_link(my_json):
            failed.append("Download link is not alive")
        if not self.validate_dates(my_json):
            failed.append("There is an issue with the dates")
        if not self.validate_model(my_json):
            failed.append("Product model is incorrect")
        return failed





