import logging
import os
from logging.config import fileConfig

from flask import Flask, request, Response
from flask_restful import Resource, Api
from pymongo import MongoClient

import utils

MONGO_CONTAINER_NAME = "yad_mongo"

app = Flask(__name__)
api = Api(app)

client = MongoClient(MONGO_CONTAINER_NAME, 27017)
db = client["database"]

fileConfig('logging_config.ini')
logger = logging.getLogger()


class Importer(Resource):
    # noinspection PyMethodMayBeStatic
    def post(self):
        """
        Handles process of new citizens insertion
        """
        json_data = request.get_json(force=True)  # force needed to handle wrong MIME types, probably useless
        if "citizens" not in json_data:
            logger.log(20, f"Got no citizens in json_data")
            return 400
        if not len(json_data["citizens"]):
            logger.log(20, f"Got len of citizens < 1")
            return 400
        if utils.broken_relatives(json_data["citizens"]):
            logger.log(20, f"Got broken relatives")
            return 400
        for citizen in json_data["citizens"]:
            if not utils.datetime_correct(citizen["birth_date"]):
                logger.log(20, f"Got broken date {citizen['birth_date']}")
                return 400
        import_id = utils.next_collection(db)
        db[str(import_id)].insert_many(json_data["citizens"])
        response = {
            "data": {
                "import_id": import_id
            }
        }
        return response, 201, {"ContentType": "application/json"}


class Patcher(Resource):
    # noinspection PyMethodMayBeStatic
    def put(self, import_id: int, citizen_id: int):
        """
        Handles process of editing citizens
        """
        json_data = request.get_json(force=True)
        if not len(json_data):
            return 400
        if not db[str(import_id)].count({"citizen_id": citizen_id}):
            return 400
        if "birth_date" in json_data:
            if not utils.datetime_correct(json_data["birth_date"]):
                return 400

        # TODO Add relatives update
        db[str(import_id)].update_one(
            {"citizen_id": citizen_id},
            {"$set": json_data}
        )
        updated_citizen = db[str(import_id)].find_one({"citizen_id": citizen_id})
        return {"data": updated_citizen}, 200, {"ContentType": "application/json"}


class DataFetcher(Resource):
    # noinspection PyMethodMayBeStatic
    def get(self, import_id: int):
        """
        Handles process of getting citizens from group
        """
        data = [element for element in db[str(import_id)].find()]
        return {"data": data}, 200, {"ContentType": "application/json"}


class BirthdaysGrouper(Resource):
    # noinspection PyMethodMayBeStatic
    def get(self, import_id: int):
        """
        Handles process of getting birthdays info
        """
        raw_data = [element for element in db[str(import_id)].find()]
        processed_data = utils.birthdays_counter(raw_data)
        return {"data": processed_data}, 200, {"ContentType": "application/json"}


class PercentileFetcher(Resource):
    # noinspection PyMethodMayBeStatic
    def get(self, import_id: int):
        # TODO
        """
        Handles percentile creation
        """
        pass


class BaseDropper(Resource):
    # noinspection PyMethodMayBeStatic
    def post(self):
        if not os.environ["TESTING"]:
            return Response(status=403)
        if os.environ["TESTING"] == "TRUE":
            for col in db.list_collection_names(filter=utils.collection_filter):
                db[col].drop()
                return 200
        else:
            return 403


api.add_resource(Importer, "/imports")
api.add_resource(Patcher, "/imports/<int:import_id>/citizens/<int:citizen_id>")
api.add_resource(DataFetcher, "/imports/<int:import_id>/citizens")
api.add_resource(BirthdaysGrouper, "/imports/<int:import_id>/citizens/birthdays")
api.add_resource(PercentileFetcher, "/imports/<int:import_id>/towns/stat/percentile/age")
api.add_resource(BaseDropper, "/dropdb")  # For testing purposes

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
