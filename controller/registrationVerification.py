from flask import  request, redirect, session
from flask import render_template
from flask import current_app as app
from model.models import *
from model.database import db


app.secret_key = 'iit madras mad1 project'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup')
def signUP():
    return redirect('/signup/user')

#--------------------------------Admin--------------------------------------------------
@app.route('/signup/admin', methods = ['POST', 'GET'])
def signupAdmin():
    if request.method == 'GET':
        return render_template('admin_signup.html')
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        admin_code = request.form.get('admin_code')
        t1 = Admins.query.filter_by(username = username).all()
        t2 = Admins.query.filter_by(email = email).all()
        if len(t1) != 0:
            return render_template('home.html', out = 'Username already exist')
        elif len(t2) != 0:
            return render_template('home.html', out = 'Email already exist')
        
        t3 = Admins()
        t3.username = username
        t3.email = email
        t3.password = password
        t3.name = name

        kee = Keys.query.get(admin_code) 

        if kee:
            kee.num_of_admins += 1
            db.session.add(t3)
            db.session.commit()
            return redirect('/login')
        else:
            return render_template('home.html', out = 'Wrong admin code')


# ------------------------------------------User---------------------------------------

@app.route('/signup/user', methods = ['POST', 'GET'])
def signupUser():
    if request.method == 'GET':
        return render_template('user_signup.html')
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        t1 = Users.query.filter_by(username = username).all()
        t2 = Users.query.filter_by(email = email).all()
        

        if len(t1) != 0:
            return render_template('home.html', out = 'Username already exist')
        elif len(t2) != 0:
            return render_template('home.html', out = 'Email already exist')

        t3 = Users()    
        t3.username = username
        t3.email = email
        t3.password = password
        t3.name = name
        db.session.add(t3)
        db.session.commit()

        return redirect('/login')
    


# --------------------------------------------Login--------------------------------------------------- 
@app.route("/login", methods = ['GET', 'POST'])
def logIn():
    if request.method == 'GET':
        if "user" in session:
            username = session['user']
            return redirect(f'/user/{username}')
        elif "admin" in session:
            username = session['admin']
            return redirect(f'/admin/{username}')
        return render_template("login.html")
    
    else:
        
        email = request.form.get('email')
        password = request.form.get('password')
        admin = request.form.get('admin')

        if admin:
            potentital_admin = Admins.query.filter_by(email = email).first()
            if not potentital_admin:
                return render_template('home.html', out = 'No Such user')
            elif potentital_admin.password == password:
                    username = potentital_admin.username
                    name = potentital_admin.name
                    session["admin"] = username
                    print(session['admin'])
                    return redirect(f'/admin/{username}')
            else:
                return render_template('home.html', out = 'Wrong password')
        else:
            potentital_user = Users.query.filter_by(email = email).first()
            if not potentital_user:
                return render_template('home.html', out = 'No Such user')
            if potentital_user.password == password:
                username = potentital_user.username
                name = potentital_user.name
                session["user"] = username
                print('from user',session['user'])
                return redirect(f'/user/{username}')
            else:
                return render_template('home.html', out = 'Wrong password')

#------------------------------------------Logout-------------------------------------------------
@app.route("/logout", methods = ['GET'])
def logOut():
    if 'user' in session:
        session.pop("user", None)
    elif 'admin' in session:
        session.pop("admin", None)
    return redirect('/login')
        