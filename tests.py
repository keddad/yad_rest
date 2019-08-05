import json
import unittest
from pathlib import Path

import requests

from app import app

collection_filter = {"name": {"$regex": r"^(?!system\.)"}}

IP = "127.0.0.1"
PORT = "8080"
LOCAL = False

class TestImporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if LOCAL:
            try:
                app.run(host="0.0.0.0", port=8080)
            except OSError:
                pass
        cls.normal_case = json.loads(Path("testing_data/0.json").read_text())
        cls.broken_rels_case = json.loads(Path("testing_data/broken_rel.json").read_text())
        cls.broken_date_case = json.loads(Path("testing_data/broken_date.json").read_text())

    def test_insertion(self) -> None:
        r = requests.post(
            f"http://{IP}:{PORT}/imports",
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
            f"http://{IP}:{PORT}/imports",
            json=self.broken_rels_case
        )
        r_data = requests.post(
            f"http://{IP}:{PORT}/imports",
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

    @classmethod
    def tearDownClass(cls) -> None:
        requests.post(f"http://{IP}:{PORT}/dropdb")

if __name__ == '__main__':
    unittest.main()
3
