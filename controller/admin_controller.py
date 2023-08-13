from flask import render_template , request, session, redirect
from flask import current_app as app
from model.models import *
from model.database import db
import matplotlib.pyplot as plt
import io
import base64


@app.route('/admin')
def whateve():
    return redirect('/login')


# -----------------------------------HomePage and create category---------------------------------
@app.route('/admin/<username>', methods = ['GET', 'POST'])
def home_admin(username):
    if "admin" not in session:
        return redirect('/login')
    
    admin = session['admin']
    admin_info = Admins.query.filter_by(username = admin).first()
    username = admin_info.username
    name = admin_info.name
    
    values = {}
    values["title"] = username + " - Home"
    values["header"] = "Welcome " + name
    values["admin"] = username
    values["name"] = name
    values['username'] = username


    category_info = Categories.query.filter_by(admin_id = admin_info.admin_id).all()
    products = {}

    for i in category_info:
        tmp = Products.query.filter_by(cat_id = i.cat_id).all()
        if i.cat_name in products.keys():
            products[i.cat_name] += tmp
        else:
            products[i.cat_name] = tmp
        
    
    if request.method == 'GET':
        return render_template('admin_dashboard.html',category_info = category_info, **values, products = products )
    else:
        isExist = Categories.query.filter_by(admin_id = admin_info.admin_id)
        for i in isExist:
            if i.cat_name == request.form['name']:
                return redirect(f'/admin/{username}')        
            
        temp = Categories()
        temp.cat_name = request.form['name']
        temp.admin_id = admin_info.admin_id
        temp.date = 0
        db.session.add(temp)
        db.session.commit()
        return redirect(f'/admin/{username}')
        

# ----------------------Delete Category--------------------------------
@app.route("/admin/<username>/delete/<cat_id>")
def deleteCategory(username,cat_id):
    if "admin" not in session or username != session['admin']:
        return redirect("/login")
    category = Categories.query.get(cat_id)
    admin_info = Admins.query.filter_by(username = session["admin"]).first()

    if category is not None and admin_info.admin_id == category.admin_id:
        db.session.delete(category)
        db.session.commit()
    return redirect(f"/admin/{username}")



#---------------------------Edit Category-----------------------------
@app.route("/admin/<username>/edit/<cat_id>", methods = ['GET','POST'])
def editCategory(cat_id,username):
    if "admin" not in session:
        return redirect("/login")
    
    admin_info = Admins.query.filter_by(username = session["admin"]).first()
    category = Categories.query.get(cat_id)

    values = {}
    values["name"] = admin_info.name
    values['username'] = session["admin"]

    if request.method == 'GET':
        if admin_info.admin_id == category.admin_id:
            return render_template("admin_editCategory.html",username = username, cat_id = cat_id,name = values["name"], title = category.cat_name)
        else:
            return redirect("/login")
    else:
        if (category) is not None:
            category.cat_name = request.form['newName']       
            db.session.commit()
        return redirect(f"/admin/{username}")
    

#--------------------------------------Summary-------------------------------------
@app.route("/admin/<username>/summary", methods = ['POST','GET'])
def summarize(username):
    if 'admin' not in session or session['admin'] != username:
        return redirect("/login")
    admn = Admins.query.filter_by(username = username).first()
    name = admn.name
    values = {}
    values["title"] = username + " - Summary"
    values["header"] = "Welcome " + name
    values["admin"] = username
    values["name"] = name
    values['username'] = username

    cats = Categories.query.filter_by(admin_id = admn.admin_id).all()
    prod = {}
    for i in cats:
        tmp = Products.query.filter_by(cat_id = i.cat_id).all()
        if i.cat_id in prod.keys():
            prod[i.cat_id] += tmp
        else:
            prod[i.cat_id] = tmp

    cat_sale = {}
    prod_sale = {}

    for i in prod:
        tmp_cat = Categories.query.get(i)
        tmp_prods = Products.query.filter_by(cat_id = i).all()

        cat_sale[tmp_cat.cat_name] = 0

        for j in tmp_prods:
            number_of_prod_sold = Orders.query.filter_by(product_id = j.product_id).all()
            prod_sale[j.product_name +' - ' + tmp_cat.cat_name] = 0

            for k in number_of_prod_sold:
                prod_sale[j.product_name + ' - ' + tmp_cat.cat_name] += k.quantity

            cat_sale[tmp_cat.cat_name] += prod_sale[j.product_name + ' - ' +tmp_cat.cat_name]
    
    # Extract data from the dictionaries
    categories = [cat for cat, value in cat_sale.items() if value != 0]
    cat_num_products_sold = [value for value in cat_sale.values() if value != 0]

    prod_products = [prod for prod, value in prod_sale.items() if value != 0]
    prod_num_products_sold = [value for value in prod_sale.values() if value != 0]



    # Create a bar plot in cat
    plt.figure(figsize=(15, 5))
    plt.bar(categories, cat_num_products_sold)
    plt.xlabel('Categories')
    plt.ylabel('Number of Products Sold')
    plt.title('Products Sold by Category')

    # Convert plot to PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    # Create a bar plot in prod
    plt.figure(figsize=(15, 5))
    plt.bar(prod_products, prod_num_products_sold)
    plt.xlabel('Products')
    plt.ylabel('Number of Products Sold')
    plt.title('Products Sold')
    
    # Convert plot to PNG image
    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    plot_url1 = base64.b64encode(img1.getvalue()).decode()

    plt.close()


    return render_template('admin_summary.html', plot_url=plot_url, plot_url1 = plot_url1, **values)