import os
import json

from google.ads.googleads.client import GoogleAdsClient

src_path = os.path.dirname(os.path.realpath(__file__))

dir_path = os.path.join(src_path, '..')

creds = {"google_ads": dir_path + "/src/creds_example/googleads.yaml"}

if not os.path.isfile(creds["google_ads"]):
    raise FileExistsError("File doesn't exists. Please create folder src/creds and put googleads.yaml file there. ")

resources = {
    "config": dir_path + "/src/config/config.json",
    "customer_ids": dir_path + "/src/config/customer_ids.json"
}

gads_client = GoogleAdsClient.load_from_storage(creds["google_ads"])

config = json.load(open(resources["config"], "r"))
customer_ids = json.load(open(resources["customer_ids"], "r"))
