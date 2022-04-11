from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from main import mysql

auth = Blueprint("auth", __name__, template_folder = "templates", static_folder='static')

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'domain' in request.form:
        
        username = request.form['username']
        password = request.form['password']
        domain = request.form['domain']

        if domain == '1':   # Student 
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM students WHERE username = % s AND password = % s', (username, password, ))
            account = cursor.fetchone()

            if account:
                session['id'] = account['studentID']
                session['name'] = account['name']

                return redirect(url_for('student.pending', session_id = session['id']))
                
            else:

                flash('Student does not exist with the entered username and password!')
        
        if domain == '2': # Admin
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM invigilators WHERE username = % s AND password = % s AND admin = "yes"', (username, password, ))
            account = cursor.fetchone()

            if account:
                session['id'] = account['invigilatorID']
                session['name'] = account['name']

                #return render_template('index.html')     # CHANGE TO ADMIN's FIRST PAGE
                return redirect(url_for('admin.IndexHome'))

            else:

                flash('Admin does not exist with the entered username and password!')

        if domain == '3': # Invigilator
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM invigilators WHERE username = % s AND password = % s AND admin = "no"', (username, password, ))
            account = cursor.fetchone()

            if account:
                session['id'] = account['invigilatorID']
                session['name'] = account['name']

                return redirect(url_for('invigilator.index'))     # CHANGE TO INVIGILATORS'S FIRST PAGE

            else:
                
                flash('Invigilator does not exist with the entered username and password!')

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(debug=True)