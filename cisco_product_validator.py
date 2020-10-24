import json
from jsonschema import validate, Draft4Validator
import re
import requests
import urllib.request
from bs4 import BeautifulSoup, SoupStrainer

class CiscoProductValidator(object):
    json_schema = None
    path_regex = None
    url_download_path = None
    first_cisco_product_release = None

    def __init__(self, schema_path: str = "expected schema.json"):

        with open(schema_path, 'r') as f:
            self.json_schema = json.load(f)

        self.path_regex = re.compile(r'^(/)?([^/\0]+(/)?)+$')

        self.url_download_path = re.compile(r'^((https|ftp|file)?([Cc])?:\/\/)?(www.)?')

        # First CISCO product was released in 1986
        self.first_cisco_product_release = 504921600

    def validate_schema(self, my_json):
        try:
            validate(my_json, self.json_schema)
            return True
        except:
            return False

    def validate_unix_path(self, my_json):
        if self.path_regex.match(my_json['path']):
            return False
        else:
            return True

    def validate_product_url(self, my_json):
        if requests.get(my_json['url']).status_code == 200:
            return True
        else:
            return False

    def validate_download_link(self, my_json):
        for item in my_json['downloads']:
            if 'all' not in item:
                continue
            self.url_download_path.match(item['all']).group()
            if requests.get(item['all']).status_code == 200:
                return True
            else:
                return False

    def validate_dates(self, my_json):
        if my_json['release'] > self.first_cisco_product_release:

            if my_json['endofsale'] is not None:

                if my_json['endofsupport'] is not None:

                    if my_json['release'] < my_json['endofsale'] < my_json['endofsupport']:
                        return True
                    else:
                        return False

                else:

                    if my_json['release'] < my_json['endofsale']:
                        return True
                    else:
                        return False

            else:

                if my_json['endofsupport'] is not None:

                    if my_json['release'] < my_json['endofsupport']:
                        return True
                    else:
                        return False
                else:
                    return False

        else:
            return False

    def validate_model(self, my_json):
        page = urllib.request.urlopen(my_json['url'])
        mybytes = page.read()
        the_html = mybytes.decode("utf8")
        page.close()
        soup = BeautifulSoup(the_html)
        model_html = str(soup.h1)
        if my_json['model'] in model_html:
            return True
        else:
            return False





