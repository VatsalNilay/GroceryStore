from flask import render_template , request, session, redirect
from flask import current_app as app
from model.models import *
from model.database import db
from sqlalchemy import and_
from datetime import datetime

# -----------------------Create Product---------------------------------
@app.route('/<username>/<cat_id>/create', methods = ['POST', 'GET'])
def createProduct(username, cat_id):
    if "admin" not in session:
        return redirect('/login')
    category = Categories.query.get(cat_id)
    admin_info = Admins.query.filter_by(username = username).first()

    #cat_id of diff admin be used for creating product
    if category.admin_id != admin_info.admin_id: 
        return redirect(f'/admin/{username}')

    if not admin_info or not category:
        return redirect('/login')

    if request.method == 'GET':
        if admin_info.username == session["admin"]:
            return render_template("admin_createProduct.html",admin = admin_info, category = category)
        else:
            return redirect('/login')
    else:
        product = Products()
        product.product_name = request.form["product_name"]
        product.unit =request.form["unit"]
        product.cat_id = cat_id
        product.price = request.form["price"]
        product.products_left = request.form["quantity"]
        product.mfc_date = request.form["mfc_date"]
        product.exp_date = request.form['exp_date']
        category.date =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.add(product)
        db.session.commit()
        return redirect(f'/admin/{username}')
    

# -----------------------Delete Product------------------------------
@app.route("/<username>/delete/<product_id>")
def delProduct(username,product_id):
    if "admin" not in session or username != session['admin']:
        return redirect("/login")
    
    product = Products.query.get(product_id)
    category = Categories.query.get(product.cat_id)
    admin = Admins.query.filter_by(username = session["admin"]).first()
    if product is None:
        return redirect("/login")
    
    if category.admin_id == admin.admin_id:
        print(product.product_name,product.product_id)
        db.session.delete(product)
        db.session.commit()
        return redirect("/login")
    else:
        return redirect("/login")

# -----------------------Edit Product------------------------------
@app.route("/<username>/edit/<product_id>", methods = ["GET","POST"])
def editProduct(username,product_id):
    if "admin" not in session or username != session['admin']:
        return redirect("/login")
    
    product = Products.query.get(product_id)
    category = Categories.query.get(product.cat_id)
    admin = Admins.query.filter_by(username = session["admin"]).first()
    if product is None:
        return redirect("/login")
    
    if request.method == "GET":
        if category.admin_id == admin.admin_id:
            product.price = round(product.price,2)
            return render_template("admin_editProduct.html", product = product, admin = admin)
        else:
            return redirect("/login")
    else:
        product.product_name = request.form["product_name"]
        product.price = request.form["price"]
        product.products_left = request.form["quantity"]
        product.mfc_date = request.form["mfc_date"]
        product.exp_date = request.form['exp_date']
        
        db.session.commit()
        return redirect("/login")
    

#---------------------------------Buy Product------------------------------
@app.route('/user/<username>/buy/<product_id>', methods = ['GET', 'POST'])
def buyproduct(username,product_id):
    if 'user' not in session or username != session['user']:
        return redirect("/login")
    
    user = session['user']
    user_info = Users.query.filter_by(username = user).first()
    username = user_info.username
    name = user_info.name

    values = {}
    values["title"] = username + " - Home"
    values["header"] = "Welcome " + name
    values["user"] = username
    values["name"] = name
    
    product = Products.query.get(product_id)

    if request.method == 'GET':
        product.price = round(product.price,2)
        return render_template("user_buyProduct.html",**values, product = product)
    else:
        uid = user_info.user_id
        exist = Cart.query.filter(and_(Cart.user_id == uid, Cart.product_id == product_id)).first()
        if exist:
            return redirect(f'/user/{username}/cart')
        cart = Cart()
        cart.user_id = user_info.user_id
        cart.product_id = product_id
        cart.quantity = request.form['quantity']

        db.session.add(cart)
        db.session.commit()
        return redirect(f"/user/{username}")



# --------------------------------Buy from Cart------------------------------------
@app.route('/user/<username>/cart/buy', methods = ['GET'])
def buyItem(username):
    if 'user' not in session or username != session['user']:
        return redirect('/login')

    user = Users.query.filter_by(username = username).first()
    item = Cart.query.filter_by(user_id = user.user_id).all()
    
    for prod in item:
        product = Products.query.get(prod.product_id)
        order = Orders()
        order.user_id = user.user_id
        order.product_id = prod.product_id
        order.quantity = prod.quantity
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        order.timedate = formatted_datetime
        product.products_left -= prod.quantity

        similarInCart = Cart.query.filter_by(product_id = prod.product_id).all()
        for x in similarInCart:
            x.quantity = product.products_left

        db.session.add(order)
        db.session.delete(prod)
        db.session.commit()
    
    return redirect("/user/{{username}}")        