import os
from flask import Flask
from model.database import db
from flask_restful import  Api
from model.models import *


current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
db.init_app(app)
app.app_context().push()



from controller import *

from api.categories import CategoriesList, CategoryDetails
api.add_resource(CategoriesList, '/api/categories')
api.add_resource(CategoryDetails, '/api/categories/<int:cat_id>')

from api.products import ProductsList, ProductsDetail
api.add_resource(ProductsList, '/api/products')
api.add_resource(ProductsDetail, '/api/products/<int:product_id>')

if __name__ == '__main__':
    app.run(
        debug=True
    )