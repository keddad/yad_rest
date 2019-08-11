import logging
import unittest
from json import loads
from pathlib import Path

import requests

collection_filter = {"name": {"$regex": r"^(?!system\.)"}}
logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)

IP = "84.201.167.25"
PORT = "8080"
LOCAL = False


def setupServer() -> None:
    if LOCAL:
        print("Tests can only be ran using a Docker container")
        raise EnvironmentError


class TestImporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        setupServer()
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
        setupServer()
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
            f"http://{IP}:{PORT}/imports/99999999/citizens"
        )
        self.assertEqual(r.status_code,
                         400,
                         msg=f"Got {r.status_code} instead of 400 while fetching")

    @classmethod
    def tearDownClass(cls) -> None:
        requests.post(f"http://{IP}:{PORT}/dropdb")


class TestPatcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        setupServer()
        cls.normal_case = loads(Path("testing_data/data_0.json").read_text())
        cls.normal_update = loads(Path("testing_data/update_0.json").read_text())
        cls.rels_update = loads(Path("testing_data/rels_update_0.json").read_text())
        cls.expected_rels_result = loads(Path("testing_data/expected_rels_up.json").read_text())
        cls.expected_normal_result = loads(Path("testing_data/expected_normal_up.json").read_text())

        r = requests.post(
            f"http://{IP}:{PORT}/imports",
            json=cls.normal_case
        )
        cls.import_id = loads(r.text)["data"]["import_id"]

    def test_update(self):
        r = requests.put(
            f"http://{IP}:{PORT}/imports/{self.import_id}/citizens/1",
            json=self.normal_update)
        self.assertDictEqual(loads(r.text),
                             self.expected_normal_result,
                             msg=f"Got wrong update response on normal update"
                             )

        self.assertEqual(r.status_code,
                         200,
                         msg=f"Got {r.status_code} instead of 200 while updating")

    def test_rels_update(self):
        r = requests.put(
            f"http://{IP}:{PORT}/imports/{self.import_id}/citizens/4",
            json=self.rels_update)

        self.assertEqual(r.status_code,
                         200,
                         msg=f"Got {r.status_code} instead of 200 while updating")

        self.assertDictEqual(loads(r.text),
                             self.expected_rels_result,
                             msg=f"Got wrong update response on relatives update")

        data_after_update = requests.get(
            f"http://{IP}:{PORT}/imports/{self.import_id}/citizens"
        )
        for citizen in loads(data_after_update.text)["data"]:
            if citizen["citizen_id"] == 1 or citizen["citizen_id"] == 2 or citizen["citizen_id"] == 5:
                self.assertIn(4,
                              citizen["relatives"])
            if citizen["citizen_id"] == 3:
                self.assertNotIn(4,
                                 citizen["relatives"])

    @classmethod
    def tearDownClass(cls) -> None:
        requests.post(f"http://{IP}:{PORT}/dropdb")


class TestRelatives(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        setupServer()
        cls.normal_case = loads(Path("testing_data/data_0.json").read_text())
        cls.normal_response = loads(Path("testing_data/birthdays_0.json").read_text())
        r = requests.post(
            f"http://{IP}:{PORT}/imports",
            json=cls.normal_case
        )
        cls.import_id = loads(r.text)["data"]["import_id"]

    def test_normal(self):
        r = requests.get(
            f"http://{IP}:{PORT}/imports/{self.import_id}/citizens/birthdays",
        )

        self.assertDictEqual(loads(r.text),
                             self.normal_response,
                             msg=f"Got wrong response on birthdays counter")

    def test_error(self):
        r = requests.get(
            f"http://{IP}:{PORT}/imports/9999999/citizens/birthdays",
        )

        self.assertEqual(r.status_code,
                         400,
                         msg=f"Got {r.status_code} instead of 400 while updating")

    @classmethod
    def tearDownClass(cls) -> None:
        requests.post(f"http://{IP}:{PORT}/dropdb")


class TestPercentile(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        setupServer()
        cls.normal_case = loads(Path("testing_data/data_0.json").read_text())
        cls.normal_response = loads(Path("testing_data/percentile_0.json").read_text())
        r = requests.post(
            f"http://{IP}:{PORT}/imports",
            json=cls.normal_case
        )
        cls.import_id = loads(r.text)["data"]["import_id"]

    def test_normal(self):
        r = requests.get(
            f"http://{IP}:{PORT}/imports/{self.import_id}/towns/stat/percentile/age",
        )

        self.assertDictEqual(loads(r.text),
                             self.normal_response,
                             msg=f"Got wrong response on birthdays counter")

    def test_error(self):
        r = requests.get(
            f"http://{IP}:{PORT}/imports/9999999/towns/stat/percentile/age",
        )

        self.assertEqual(r.status_code,
                         400,
                         msg=f"Got {r.status_code} instead of 400 while updating")

    @classmethod
    def tearDownClass(cls) -> None:
        requests.post(f"http://{IP}:{PORT}/dropdb")


if __name__ == '__main__':
    unittest.main()
