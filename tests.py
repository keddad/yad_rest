import json
import unittest
from pathlib import Path

import requests
from pymongo import MongoClient

from app import app

filter = {"name": {"$regex": r"^(?!system\.)"}}


class TestImporter(unittest.TestCase):
    def setUp(self) -> None:
        try:
            app.run(host="0.0.0.0", port=8080)
        except OSError:
            pass
        self.normal_case = json.loads(Path("testing_data/0.json").read_text())
        self.broken_rels_case = json.loads(Path("testing_data/broken_rel.json").read_text())
        self.broken_date_case = json.loads(Path("testing_data/broken_date.json").read_text())

    def test_insertion(self) -> None:
        r = requests.post(
            "http://localhost/imports:8080",
            json=self.normal_case
        )
        self.assertEqual(r.status_code,
                         201,
                         msg=f"Got {r.status_code} instead of 201"
                         )
        returned_data = json.loads(r.text)
        self.assertIs(returned_data["data"]["import_id"],
                      int,
                      msg=f"Got {type(returned_data['data']['import_id'])} instead of int in response"
                      )

    def check_errors(self) -> None:
        r_rels = requests.post(
            "http://localhost/imports:8080",
            json=self.broken_rels_case
        )
        r_data = requests.post(
            "http://localhost/imports:8080",
            json=self.broken_date_case
        )
        self.assertEqual(r_rels.status_code,
                         400,
                         msg=f"Got {r_rels.status_code} instead of 400"
                         )
        self.assertEqual(r_data.status_code,
                         400,
                         msg=f"Got {r_data.status_code} instead of 400"
                         )

    def tearDown(self) -> None:
        client = MongoClient("localhost", 27017)
        db = client["database"]
        for col in db.list_collection_names(filter=filter):
            db[col].drop()
