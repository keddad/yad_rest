from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("loaclhost", 27017)
db = client["database"]


class Importer(Resource):
    def post(self):
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
        db["collections"].insert_one(json_data)
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
    def patch(self, import_id: int, citizen_id: int):
        """
        Handles process of editing citizens
        """
        pass


class DataFetcher(Resource):
    def get(self, import_id: int):
        """
        Handles process of getting citizens from group
        """
        pass


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
