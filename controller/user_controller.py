from flask import render_template , request, session, redirect
from flask import current_app as app
from model.models import *
from model.database import db
from sqlalchemy import and_ , desc


@app.route('/user')
def whatev():
    return redirect('/login')

# -----------------------------User Dashboard-----------------------------------
@app.route('/user/<username>', methods = ['GET', 'POST'])
def home_user(username):
    if "user" not in session:
        return redirect('/login')
    
    user = session['user']
    user_info = Users.query.filter_by(username = user).first()
    username = user_info.username
    name = user_info.name
    values = {}
    values["title"] = username + " - Home"
    values["header"] = "Welcome " + name
    values["user"] = username
    values["name"] = name
    cat = Categories.query.order_by(Categories.date.desc()).all()
    products = {}

    for i in cat:
        products[i.cat_name] = []

    for i in cat:
        tmp = Products.query.filter_by(cat_id = i.cat_id).all()
        if tmp:
            tmp.reverse()
            products[i.cat_name] += tmp
    
    to_delete = []
    for i in products:
        if len(products[i]) == 0:
            to_delete.append(i)
    
    for i in to_delete:
        del products[i]

    if request.method == 'GET':
        return render_template('user_dashboard.html', **values, products = products)
    else:
        if request.form['filter'] == 'product':
            prod = {}
            tmp_prod = Products.query.filter_by(product_name = request.form['query']).all()
            for i in tmp_prod:
                tmp_cat = Categories.query.get(i.cat_id)
                if tmp_cat.cat_name not in prod.keys():
                    prod[tmp_cat.cat_name] = [i]
                else:
                    prod[tmp_cat.cat_name] += [i]
            
            if len(prod) != 0:
                return render_template('user_dashboard.html', **values, products = prod)
            else:
                return render_template('user_dashboard.html', **values, products = products)

        
        elif request.form['filter'] == 'category':
            cat = Categories.query.filter_by(cat_name = request.form['query']).all()
            if not cat:
                return render_template('user_dashboard.html', **values, products = products)
            prod = Products.query.filter_by(cat_id = cat[0].cat_id)
            products_cat = {}
            if not prod:
                return render_template('user_dashboard.html', **values, products = products)

            products_cat[cat[0].cat_name] = []
            
            for i in cat:
                tmp_product = Products.query.filter_by(cat_id = i.cat_id).all()
                for j in tmp_product:
                    products_cat[i.cat_name] += [j]
            if len(products_cat) != 0:
                return render_template('user_dashboard.html', **values, products = products_cat)
            else:
                return render_template('user_dashboard.html', **values, products = products)

        elif request.form['filter'] == 'price':
            products_price = {}
            tmp_product = Products.query.filter_by(price = request.form['query']).all()
            for i in tmp_product:
                tmp_cat = Categories.query.get(i.cat_id)
                if tmp_cat.cat_name in products_price.keys():
                    products_price[tmp_cat.cat_name] += [i]
                else:
                    products_price[tmp_cat.cat_name] = [i]
            if len(products_price) != 0:
                return render_template('user_dashboard.html', **values, products = products_price)
            else:
                return render_template('user_dashboard.html', **values, products = products)

        elif request.form['filter'] == 'mfc_date':
            products_mfc = {}
            tmp_product = Products.query.filter_by(mfc_date = request.form['date']).all()
            for i in tmp_product:
                tmp_cat = Categories.query.get(i.cat_id)
                if tmp_cat.cat_name in products_mfc.keys():
                    products_mfc[tmp_cat.cat_name] += [i]
                else:
                    products_mfc[tmp_cat.cat_name] = [i]
            if len(products_mfc) != 0:
                return render_template('user_dashboard.html', **values, products = products_mfc)
            else:
                return render_template('user_dashboard.html', **values, products = products)

#----------------------------Cart---------------------------------
@app.route('/user/<username>/cart', methods = ['GET', 'POST'])    
def usercart(username):
    if 'user' not in session:
        return redirect('/login')
    
    if session['user'] != username:
        x = session['user']
        return redirect(f'/user/{x}')
    
    user = Users.query.filter_by(username = username).first()
    values = {}
    values["title"] = username + " - Home"
    values["header"] = "Welcome " + user.name
    values["user"] = username
    values["name"] = user.name
    cart = Cart.query.filter_by(user_id = user.user_id).all()

    products = []
    if request.method == 'GET':
        amt = 0
        for i in cart:
            tmp = {}
            prod = Products.query.get(i.product_id)
            prod.price = round(prod.price,2)
            cat = Categories.query.get(prod.cat_id)
            amt += (prod.price * i.quantity)
            tmp["Category"] = cat.cat_name
            tmp["Product"] = prod.product_name
            tmp['Price'] = prod.price
            tmp['Quantity'] = i.quantity
            tmp['Unit'] = prod.unit
            tmp['product_id'] = i.product_id
            products.append(tmp)
            
        amt = round(amt,2)
        return render_template("user_cart.html",**values, product = products ,amount = amt)
    else:
        return redirect('/user/{{username}}')



#----------------------------Delete from cart ------------------------------
@app.route('/user/<username>/cart/delete/<product_id>')
def delFromCart(username,product_id):
    if 'user' not in session:
        return redirect("/login")
    
    if session['user'] != username:
        x = session['user']
        return redirect(f"/user/{x}")
    user = Users.query.filter_by(username = username).first()
    
    item = Cart.query.filter(and_(Cart.user_id == user.user_id, Cart.product_id == product_id)).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    
    return redirect(f'/user/{username}/cart')

# --------------------------------Modify Item - Cart-----------------------------------
@app.route("/user/<username>/cart/modify/<product_id>",methods = ['GET', 'POST'])
def modifyItem(username,product_id):
    if 'user' not in session or session['user'] != username:
        return redirect("/login")
    
    prod = Products.query.get(product_id)
    user_info = Users.query.filter_by(username = username).first()
    currCart = Cart.query.filter(and_(Cart.user_id == user_info.user_id, Cart.product_id == product_id)).first()

    name = user_info.name
    values = {}
    values["title"] = username + " - Home"
    values["header"] = "Welcome " + name
    values["user"] = username
    values["name"] = name
    values["quantity"] = currCart.quantity
    values['price'] = round(currCart.quantity*prod.price,2)
    prod.price = round(prod.price,2)
    if request.method == 'GET':
        return render_template("user_modifyItem.html", **values, product = prod)
    else:
        currCart.quantity = request.form['quantity']
        db.session.commit()
        return redirect(f"/user/{username}/cart")


#---------------------------------Profile---------------------------------------
@app.route("/user/<username>/profile")
def profilePage(username):
    if 'user' not in session or username != session['user']:
        return redirect("/login")
    
    user = Users.query.filter_by(username= username).first()
    order = Orders.query.filter_by(user_id=user.user_id).order_by(desc(Orders.timedate)).all()
    orders = []

    for i in order:
        tmp = {}
        tmp_prod = Products.query.get(i.product_id)
        tmp_cat = Categories.query.get(tmp_prod.cat_id)
        tmp['category_name'] = tmp_cat.cat_name
        tmp['product_name'] = tmp_prod.product_name
        tmp['price'] = round(tmp_prod.price,2)
        tmp['unit'] = tmp_prod.unit
        tmp['quantity'] = i.quantity
        orders.append(tmp)
 
    values = {}
    values["title"] = username + " - Home"
    values["header"] = "Welcome " + user.name
    values["user"] = username
    values["name"] = user.name
    return render_template('user_profile.html', **values, orders = orders )

        