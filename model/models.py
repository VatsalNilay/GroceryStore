from .database import db

class Keys(db.Model):
    __tablename__ = "keys"
    admin_keys = db.Column(db.Integer, primary_key = True)
    num_of_admins = db.Column(db.Integer, nullable = False)

class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)
    email = db.Column(db.String,unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)
    name = db.Column(db.String, unique = True, nullable = False)

    cart = db.relationship('Cart', backref = 'user',cascade='all, delete')
    order = db.relationship('Orders', backref = 'user',cascade='all, delete')


class Admins(db.Model):
    __tablename__ = "admins"
    admin_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)
    email = db.Column(db.String,unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)
    name = db.Column(db.String, unique = True, nullable = False)

    categories = db.relationship('Categories', backref='admin',cascade='all, delete')


class Categories(db.Model):
    __tablename__ = "categories"
    cat_id = db.Column(db.Integer,autoincrement = True,  primary_key = True)
    cat_name = db.Column(db.String, unique = True, nullable = False)
    date = db.Column(db.String,  nullable = False)

    admin_id = db.Column(db.Integer,db.ForeignKey('admins.admin_id'),nullable=False)
    products = db.relationship('Products', backref='categories',cascade='all, delete')


class Products(db.Model):
    __tablename__ = "products"
    product_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    product_name = db.Column(db.String, nullable = False)
    price = db.Column(db.Numeric, nullable = False)
    unit = db.Column(db.String, nullable = False)
    products_left = db.Column(db.Integer, nullable = False)
    mfc_date = db.Column(db.String, nullable = False)
    exp_date = db.Column(db.String)

    cat_id = db.Column(db.Integer, db.ForeignKey('categories.cat_id'), nullable = False)
    cart  = db.relationship('Cart', backref = 'products' , cascade='all, delete-orphan')
    order = db.relationship('Orders', backref = 'products', cascade='all, delete-orphan')

class Cart(db.Model):
    __tablename__ = "cart"
    user_id = db.Column(db.Integer,db.ForeignKey('users.user_id',ondelete='CASCADE'),primary_key = True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'),primary_key = True )
    quantity = db.Column(db.Integer,nullable = False)

class Orders(db.Model):
    __tablename__ = "orders"
    user_id = db.Column(db.Integer,db.ForeignKey('users.user_id'),primary_key = True, nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'),primary_key = True , nullable = False)
    timedate = db.Column(db.String, primary_key = True, nullable = False)
    quantity = db.Column(db.Integer,nullable = False)