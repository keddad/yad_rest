from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
from pymongo import MongoClient

import utils

app = Flask(__name__)
api = Api(app)

client = MongoClient("localhost", 27017)
db = client["database"]


class Importer(Resource):
    # noinspection PyMethodMayBeStatic
    def post(self) -> Response:
        """
        Handles process of new citizens insertion
        """
        json_data = request.get_json(force=True)  # force needed to handle wrong MIME types, probably useless
        if "citizens" not in json_data:
            return Response(status=400)
        if not len(json_data["citizens"]):
            return Response(status=400)
        if utils.broken_relatives(json_data["citizens"]):
            return Response(status=400)
        import_id = utils.next_collection(db)
        for citizen in json_data["citizens"]:
            db[import_id].insert_one(citizen)
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
    def patch(self, import_id: int, citizen_id: int) -> Response:
        """
        Handles process of editing citizens
        """
        json_data = request.get_json(force=True)
        if not len(json_data):
            return Response(status=400)
        if not db[import_id].count({"citizen_id": citizen_id}):
            return Response(status=400)
        # TODO Add relatives update
        db[import_id].update_one(
            {"citizen_id": citizen_id},
            {"$set": json_data}
        )
        updated_citizen = db[import_id].find_one({"citizen_id": citizen_id})
        return Response(
            response=jsonify(updated_citizen),
            status=200,
            mimetype="application/json"
        )


class DataFetcher(Resource):
    # noinspection PyMethodMayBeStatic
    def get(self, import_id: int):
        """
        Handles process of getting citizens from group
        """
        data = [element for element in db[import_id].find()]
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
        raw_data = [element for element in db[import_id].find()]
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


api.add_resource(Importer, "/imports")
api.add_resource(Patcher, "/imports/<int:import_id>/citizens/<int:citizen_id>")
api.add_resource(DataFetcher, "/imports/<int:import_id>/citizens")
api.add_resource(BirthdaysGrouper, "/imports/<int:import_id>/citizens/birthdays")
api.add_resource(PercentileFetcher, "/imports/<int:import_id>/citizens/birthdays")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
