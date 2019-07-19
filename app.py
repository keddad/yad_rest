from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
from pymongo import MongoClient
import util

app = Flask(__name__)
api = Api(app)

client = MongoClient("loaclhost", 27017)
db = client["database"]


class Importer(Resource):
    def post(self) -> Response:
        """
        Handles process of new citizens insertion
        """
        json_data = request.get_json(force=True)  # force needed to handle wrong MIME types, probably useless
        if "citizens" not in json_data:
            return Response(status=400)
        if not len(json_data["citizens"]):
            return Response(status=400)
        import_id = db["collections"].count() + 1
        json_data["import_id"] = import_id
        for citizen in json_data["citizens"]:
            citizen["import_id"] = import_id
            db["collections"].insert_one(citizen)
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
    def patch(self, import_id: int, citizen_id: int) -> Response:
        """
        Handles process of editing citizens
        """
        json_data = request.get_json(force=True)
        if not len(json_data):
            return Response(status=400)
        db["collections"].update_one(
            {"import_id": import_id, "citizen_id": citizen_id},
            {"$set": json_data}
        )
        updated_citizen = db["collections"].find_one({"import_id": import_id, "citizen_id": citizen_id})
        del updated_citizen["import_id"]  # Этот костыль вызван моим нежеланием понимать поиск по вложенным документам
        return Response(
            response=jsonify(updated_citizen),
            status=200,
            mimetype="application/json"
        )


class DataFetcher(Resource):
    def get(self, import_id: int):
        """
        Handles process of getting citizens from group
        """
        data = list()
        for element in db["collections"].find({"import_id": import_id}):
            data.insert(element)
        for element in data:
            del element["import_id"]
        return Response(
            response=jsonify({"data": data}),
            status=200,
            mimetype="application/json"
        )


class BirthdaysGrouper(Resource):
    def get(self, import_id: int):
        """
        Handles process of getting birthdays info
        """
        pass


class PercentileFetcher(Resource):
    def get(self, import_id: int):
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
