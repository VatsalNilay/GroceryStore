from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_restful import Resource, fields, marshal_with, reqparse, marshal, abort
from model.database import db
from model.models import *
# import datetime
# Resource for Categories
category_fields = {
    'cat_id': fields.Integer,
    'cat_name': fields.String,
    'admin_id': fields.Integer,
    'date': fields.String
}
# Request parser for input validation
category_parser = reqparse.RequestParser()
category_parser.add_argument('cat_name', type=str, required=True, help='Category name is required')
category_parser.add_argument('admin_id', type=int, required=True, help='Admin ID is required')


class CategoriesList(Resource):
    @marshal_with(category_fields)
    def get(self):
        category = Categories.query.all()
        if category:
            return  category,200
        abort(404, message=f" No Categories found")

    @marshal_with(category_fields)
    def post(self):
        args = category_parser.parse_args()
        
        isExist2 = Admins.query.get(args['admin_id'])
        if not isExist2:
            abort(404, message=f"Admin '{args['admin_id']}' doesn't exist")
        newCat = Categories()
        newCat.cat_name = args['cat_name']
    
        newCat.admin_id = args['admin_id']
        newCat.date = 0
    
        db.session.add(newCat)
        db.session.commit()
        return newCat ,201






class CategoryDetails(Resource):

    @marshal_with(category_fields)
    def get(self, cat_id):
        category = Categories.query.get(cat_id)
        if not category:
            abort(404, message="Category {} doesn't exist".format(cat_id))
        return category, 200

    @marshal_with(category_fields)
    def put(self, cat_id):
        category = Categories.query.get(cat_id)
        if not category:
            abort(404, message="Category {} doesn't exist".format(cat_id))
        category.cat_name = request.get_json()['cat_name']
        db.session.commit()
        return category, 201
        

    def delete(self, cat_id):
        category = Categories.query.get(cat_id)
        if category:
            cat = {}
            cat['cat_id'] = category.cat_id
            cat['cat_name'] = category.cat_name
            cat['admin_id'] = category.admin_id
            cat['date'] = category.date
            db.session.delete(category)
            db.session.commit()
            return cat, 204
        abort(404, message="Category {} doesn't exist".format(cat_id))