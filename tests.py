import logging
import unittest
from json import loads
from pathlib import Path

import requests

from app import app

collection_filter = {"name": {"$regex": r"^(?!system\.)"}}
logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)

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
        cls.normal_case = loads(Path("testing_data/data_0.json").read_text())
        cls.broken_rels_case = loads(Path("testing_data/broken_rel.json").read_text())
        cls.broken_date_case = loads(Path("testing_data/broken_date.json").read_text())

    def test_insertion(self) -> None:
        r = requests.post(
            f"http://{IP}:{PORT}/imports",
            json=self.normal_case
        )
        self.assertEqual(r.status_code,
                         201,
                         msg=f"Got {r.status_code} instead of 201"
                         )
        returned_data = loads(r.text)
        self.assertIs(type(returned_data["data"]["import_id"]),
                      int,
                      msg=f"Got {type(returned_data['data']['import_id'])} instead of int in response"
                      )

    def test_check_errors(self) -> None:
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
                         msg=f"Got {r_rels.status_code} instead of 400 on relatives check"
                         )
        self.assertEqual(r_data.status_code,
                         400,
                         msg=f"Got {r_data.status_code} instead of 400 on date check"
                         )

    @classmethod
    def tearDownClass(cls) -> None:
        requests.post(f"http://{IP}:{PORT}/dropdb")


class TestFetcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if LOCAL:
            try:
                app.run(host="0.0.0.0", port=8080)
            except OSError:
                pass
        cls.normal_case = loads(Path("testing_data/data_0.json").read_text())
        r = requests.post(
            f"http://{IP}:{PORT}/imports",
            json=cls.normal_case
        )
        cls.import_id = loads(r.text)["data"]["import_id"]
        cls.normal_response = loads(Path("testing_data/fetcher_response_0.json").read_text())

    def test_getter(self):
        r = requests.get(
            f"http://{IP}:{PORT}/imports/{self.import_id}/citizens"
        )
        self.assertEqual(r.status_code,
                         200,
                         msg=f"Got {r.status_code} instead of 200 while fetching")
        self.assertEqual(loads(r.text),
                         self.normal_response,
                         msg="Got wrong response")

    def test_wrong_id(self):
        r = requests.get(
            f"http://{IP}:{PORT}/imports/-42/citizens"
        )
        self.assertEqual(r.status_code,
                         400,
                         msg=f"Got {r.status_code} instead of 400 while fetching")

    @classmethod
    def tearDownClass(cls) -> None:
        requests.post(f"http://{IP}:{PORT}/dropdb")


if __name__ == '__main__':
    unittest.main()
