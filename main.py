from flask import Flask, render_template, redirect, url_for
from flask_mysqldb import MySQL
from flask_cors import CORS

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your secret key'

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'fyp'
    #app.config['MYSQL_DB'] = 'crud'

    mysql.init_app(app)

    from auth.auth import auth
    from student.student import student
    from admin.admin import admin
    #from invigilator.invigilator import invigilator

    app.register_blueprint(auth, url_prefix = "/auth")
    app.register_blueprint(student, url_prefix = "/student")
    app.register_blueprint(admin, url_prefix = "/admin")
    #app.register_blueprint(invigilator, url_prefix = "/invigilator")

    @app.route('/')
    def default_page():
        return redirect(url_for('auth.login'))

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
    #create_app().run(host='0.0.0.0', debug=True)