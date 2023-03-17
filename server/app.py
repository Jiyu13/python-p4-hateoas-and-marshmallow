#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# ---------------------------------------------------------------------------------
# 1. initialize Marshmallow with an instance of the Flask application
ma = Marshmallow(app)


# 2. configure the serialiser's schema
# inherites from a SQLAlchemySchema parent class, allows us to autogenerate some attrs using SQLAlchemy's Model class
class NewsletterSchema(ma.SQLAlchemySchema):     
    class Meta:
        model = Newsletter
    # the only two attrs that appear when look ar newsletters
    title = ma.auto_field()
    published_at = ma.auto_field()

    # 3. set up URLs for single records and for collection on each record
    # help users navigate our API
    # are set for lowercase versions of view class/function names
    # extra column in the browser with "collection" and "self" as keys
    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "newsletterbyid",
                values=dict(id="<id>")),
            "collection": ma.URLFor("newsletters"),
        }
    )
    # =>
    # "url": {
    #   "collection": "/newsletters",
    #   "self": "/newsletters/1"
    # }

# 4. initialize schema for single records and for multiple records
newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many=True)

api = Api(app)
# ---------------------------------------------------------------------------------


class Index(Resource):

    def get(self):
        response_dict = {
            "index": "Welcome to the Newsletter RESTful API",
        }
        response = make_response(response_dict, 200,)
        return response

api.add_resource(Index, '/')


class Newsletters(Resource):
    # ----------------------------------------------------------------------------------
    # def get(self):
        
    #     response_dict_list = [n.to_dict() for n in Newsletter.query.all()]
    #     response = make_response(response_dict_list, 200,)
    #     return response

    def get(self):
        newsletters = Newsletter.query.all()
        response = make_response(
            # get the JSON for multiple newsletter records into the response obj, then return it
            # get multiple newsletters, so use  newsletters_schema
            newsletters_schema.dump(newsletters),
            200,
        )
        return response
    # ----------------------------------------------------------------------------------


    def post(self):
        
        new_record = Newsletter(
            title=request.form['title'],
            body=request.form['body'],
        )

        db.session.add(new_record)
        db.session.commit()

        # response_dict = new_record.to_dict()
        # only post one record, use  newsletter_schema
        response_dict = newsletter_schema.dummp(new_record)
        response = make_response(response_dict, 201,)
        return response

api.add_resource(Newsletters, '/newsletters')


class NewsletterByID(Resource):

    def get(self, id):

        newsletter = Newsletter.query.filter_by(id=id).first()
        # response_dict = newsletter.to_dict()
        response_dict = newsletter_schema.dump(newsletter)
        response = make_response(response_dict, 200,)
        return response

    def patch(self, id):

        record = Newsletter.query.filter_by(id=id).first()
        for attr in request.form:
            setattr(record, attr, request.form[attr])

        db.session.add(record)
        db.session.commit()

        # response_dict = record.to_dict()
        response_dict = newsletter_schema.dump(record)
        response = make_response(
            response_dict,
            200
        )

        return response

    def delete(self, id):

        record = Newsletter.query.filter_by(id=id).first()
        
        db.session.delete(record)
        db.session.commit()

        response_dict = {"message": "record successfully deleted"}

        response = make_response(
            response_dict,
            200
        )

        return response

api.add_resource(NewsletterByID, '/newsletters/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)