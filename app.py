import logging
import os
from json import dumps as jsonify
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
            logger.log(30, f"Got no citizens in json_data")
            return Response(status=400)
        if not len(json_data["citizens"]):
            logger.log(30, f"Got len of citizens < 1")
            return Response(status=400)
        if utils.broken_relatives(json_data["citizens"]):
            logger.log(30, f"Got broken relatives")
            return Response(status=400)
        for citizen in json_data["citizens"]:
            if not utils.datetime_correct(citizen["birth_date"]):
                logger.log(30, f"Got broken date {citizen['birth_date']}")
                return Response(status=400)
        import_id = utils.next_collection(db)
        db[str(import_id)].insert_many(json_data["citizens"])
        logger.log(30, f"Processed /imports normally")
        return Response(
            response=jsonify({
                "data": {
                    "import_id": import_id
                }
            }),
            status=201,
            mimetype="application/json"
        )


class Patcher(Resource):
    # noinspection PyMethodMayBeStatic
    def put(self, import_id: int, citizen_id: int) -> Response:
        """
        Handles process of editing citizens
        """
        json_data = request.get_json(force=True)
        if not len(json_data):
            return Response(status=400)
        if not db[str(import_id)].count({"citizen_id": citizen_id}):
            return Response(status=400)
        if "birth_date" in json_data:
            if not utils.datetime_correct(json_data["birth_date"]):
                return Response(status=400)

        # TODO Add relatives update
        db[str(import_id)].update_one(
            {"citizen_id": citizen_id},
            {"$set": json_data}
        )
        updated_citizen = db[str(import_id)].find_one({"citizen_id": citizen_id})
        return Response(
            response=jsonify({"data": updated_citizen}),
            status=200,
            mimetype="application/json"
        )


class DataFetcher(Resource):
    # noinspection PyMethodMayBeStatic
    def get(self, import_id: int):
        """
        Handles process of getting citizens from group
        """
        data = [element for element in db[str(import_id)].find()]
        return Response(
            response=jsonify({"data": data}),
            status=200,
            mimetype="application/json"
        )


class BirthdaysGrouper(Resource):
    # noinspection PyMethodMayBeStatic
    def get(self, import_id: int):
        """
        Handles process of getting birthdays info
        """
        raw_data = [element for element in db[str(import_id)].find()]
        processed_data = utils.birthdays_counter(raw_data)
        return Response(
            response=jsonify(processed_data),
            status=200,
            mimetype="application/json"
        )


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
