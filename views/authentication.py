from flask import (
    request, make_response, render_template, redirect
)
from os import access
from models import User
import flask_jwt_extended
import datetime

def logout():
    # hint:  https://dev.to/totally_chase/python-using-jwt-in-cookies-with-a-flask-app-and-restful-api-2p75
    response = make_response(redirect('/login', 302))
    flask_jwt_extended.unset_jwt_cookies(response)
    return response

def login():
    if request.method == 'POST':
        # authenticate user here. If the user sent valid credentials, set the
        # JWT cookies:
        # https://flask-jwt-extended.readthedocs.io/en/3.0.0_release/tokens_in_cookies/
        
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username = username).first()
        if not user:
            return render_template('login.html', message='Username not found! Please try again')

        if user.check_password(password):
            access_token = flask_jwt_extended.create_access_token(identity = user.id,expires_delta=datetime.timedelta(seconds=10))
            response = make_response(redirect('/',302))
            flask_jwt_extended.set_access_cookies(response,access_token)
            return response
        else:
            return render_template(
            'login.html', 
            message='Incorrect password! Please try again'
        )
    else:
        return render_template(
            'login.html'
        )

def initialize_routes(app):
    app.add_url_rule('/login', 
        view_func=login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', view_func=logout)