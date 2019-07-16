from flask import Flask
from flask_restful import Resource, Api
import pymongo

app = Flask(__name__)
api = Api(app)


class Importer(Resource):
    def post(self) -> None:
        """
        Handles process of new citizens insertion
        """
        pass


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
