#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Home(Resource):
    def get(self):
        pass

class Campers(Resource):
    def get(self):
        campers = Camper.query.all()
        camper_dict = [camper.to_dict(rules=('-signups',)) for camper in campers]
        return camper_dict, 200

    def post(self):
        try:
            new_camper = Camper(
            name = request.json['name'],
            age = request.json['age'])
            
            db.session.add(new_camper)
            db.session.commit()

            new_camper_dict = new_camper.to_dict(rules=('-signups',))

            return new_camper_dict, 201
        
        except Exception as exc:
            return {'errors': f'{exc}'}, 400


class CampersByID(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            return camper.to_dict(), 200
        
        return {'error': 'Camper not found'}, 404

    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            try:
                for attr in request.json:
                    setattr(camper, attr, request.json[attr])
                
                db.session.add(camper)
                db.session.commit()

                return camper.to_dict(rules=('-signups',)), 202
            except Exception as exc:
                # return {'errors': f'{exc}'}, 400
                return {'errors': ['validation errors']}, 400
        
        return {'error': 'Camper not found'}, 404

class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        if activities:
            activities_dict = [activity.to_dict(rules=('-signups', '-campers')) for activity in activities]
            return activities_dict, 200
        
        return {'errors': 'No activities found'}, 404


class ActivitiesByID(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()

            return {}, 204
        return {'error': 'Activity not found'}, 404

class Signups(Resource):
    def post(self):
        try:
            new_signup = Signup(
                camper_id = request.json['camper_id'],
                activity_id = request.json['activity_id'],
                time = request.json['time']
            )

            db.session.add(new_signup)
            db.session.commit()

            return new_signup.to_dict(), 201

        except Exception as exc:
            # return {'errors': f'{exc}'}, 400
            return {'errors': ['validation errors']}, 400

api.add_resource(Home, '/')
api.add_resource(Campers, '/campers')
api.add_resource(CampersByID, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(ActivitiesByID, '/activities/<int:id>')
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
