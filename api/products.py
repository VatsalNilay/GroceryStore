from flask import request
from flask_restful import Resource, fields, marshal_with, reqparse, marshal, abort
from model.database import db
from model.models import *
from datetime import datetime


product_parser = reqparse.RequestParser()
product_parser.add_argument('product_name', type=str, required=True, help='Product name is required')
product_parser.add_argument('price', type=float, required=True, help='Price is required')
product_parser.add_argument('unit', type=str, required=True, help='Unit is required')
product_parser.add_argument('quantity', type=int, required=True, help='Quantity is required')
product_parser.add_argument('mfc_date', type=str, required=True, help='Manufacturing date is required')
product_parser.add_argument('exp_date', type=str)
product_parser.add_argument('cat_id', type=int, required=True, help='Category ID is required')

product_fields = {
    'product_id': fields.Integer,
    'cat_id': fields.Integer,
    'product_name': fields.String,
    'price': fields.Float,
    'unit': fields.String,
    'products_left': fields.Integer,
    'mfc_date': fields.String,
    'exp_date': fields.String
}

class ProductsList(Resource):
    @marshal_with(product_fields)
    def get(self):
        product = Products.query.all()
        if product:
            return product,200
        abort(404, message=f" No Proucts found")

    @marshal_with(product_fields)
    def post(self):
        args = product_parser.parse_args()
        isExist = Categories.query.get(args['cat_id'])
        if not isExist:
            abort(404, message=f"Category '{args['cat_id']}' doesn't exists")
        
        newProd = Products()
        newProd.product_name = args['product_name']
        newProd.price = args['price']
        newProd.cat_id = args['cat_id']
        newProd.products_left = args['quantity']
        newProd.unit= args['unit']
        newProd.mfc_date = args['mfc_date']
        if args['exp_date'] is None or args['exp_date'] == '0':
            newProd.exp_date = ''
        else:
            newProd.exp_date = args['exp_date']
        isExist.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.add(newProd)
        db.session.commit()
        return newProd,201



class ProductsDetail(Resource):
    @marshal_with(product_fields)
    def get(self, product_id):
        prod = Products.query.get(product_id)
        if not prod:
            abort(404, message=f"Product '{product_id}' doesn't exists")
        return prod,200
    
    
    @marshal_with(product_fields)
    def put(self, product_id):
        prod = Products.query.get(product_id)
        if not prod:
            abort(404, message="Product {} doesn't exist".format(product_id))
        cat = Categories.query.get(prod.cat_id)
        
        prod.product_name = request.get_json()['product_name']
        prod.price = request.get_json()['price']
        prod.products_left = request.get_json()['quantity']
        prod.mfc_date = request.get_json()['mfc_date']
        if request.get_json()['exp_date'] != "0":
            prod.exp_date = request.get_json()['exp_date']
        cat.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        db.session.commit()
        return prod, 201



    def delete(self, product_id):
        product = Products.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return '', 204
        abort(404, message=f"Product '{product_id}' doesn't exists")
