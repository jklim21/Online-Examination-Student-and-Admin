from fileinput import filename
from pickletools import string1
from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_mysqldb import MySQL, MySQLdb
from werkzeug.utils import secure_filename
import os 
import base64
import csv 
from main import mysql


#making admin.py part of the Blueprint
admin = Blueprint("admin", __name__, static_folder = "static", template_folder="templates")


#app routes for indexadmin.html 
@admin.route("/")
def IndexHome():

    return render_template('indexadmin.html')


#app routes for viewfile.html 
@admin.route("/view")
def View():

    return render_template('viewfile.html')

#app routes for gradescenter.html 
@admin.route("/grades")
def Grades():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM examinations")
    courselist = cur.fetchall()
    cur.close()

    return render_template('gradecenter.html', courselist = courselist)


#app routes for updateexam.html 
#app route for connecting - SQL done
@admin.route("/updateexam")
def Index():

    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM examinations")
    data = cur.fetchall()
    cur.close()

    return render_template('updateexam.html', examinations = data)


#app route for inserting - SQL done
@admin.route('/insert', methods = ['POST'])
def insert():
    if request.method == 'POST':
        flash("New Examination Record has been added successfully.")

        
        courseCode = request.form['coursecode']
        courseName = request.form['coursename']
        examDate = request.form['date']
        startTime = request.form['startTime']
        endTime = request.form['endTime']
        Duration = request.form['Duration']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO examinations(courseCode, courseName, date, start, end, duration) VALUES (%s, %s, %s, %s ,%s, %s)", (courseCode, courseName, examDate, startTime, endTime, Duration))
        mysql.connection.commit()
        return redirect(url_for('admin.Index'))


# app route for updating (for editting) - SQL done
@admin.route('/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        id_data = request.form['examID']
        courseCode = request.form['coursecode']
        courseName = request.form['courseName']
        examDate = request.form['date']
        startTime = request.form['startTime']
        endTime = request.form['endTime']
        # examPaper = request.form['examPaper']
        # studentNamelist = request.form['studentNamelist']
        # invigilatorNamelist = request.form['invigilatortNamelist'] 

        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE examinations
               SET courseCode=%s, courseName=%s, date=%s, start=%s, end=%s
               WHERE examID=%s
            """, (courseCode, courseName, examDate, startTime, endTime, id_data))
        flash("Examination Record Updated Successfully.")
        mysql.connection.commit()
        return redirect(url_for('admin.Index'))

#app route for updating for uploading exam paper once
@admin.route('/uploadpaper', methods=['POST','GET'])
def uploadpaper():
    if request.method == 'POST':
      files = request.files.getlist('examPaper[]')
      id_data = request.form['examID']
      for file in files:
        #updating exam paper column 
        cur = mysql.connection.cursor()
        blobfile = file.read()
        cur.execute("UPDATE examinations SET examPaper=%s WHERE examID=%s", (blobfile, id_data))
        mysql.connection.commit()
        cur.close  

        
      flash('Exam Paper is successfully uploaded.')

    return redirect(url_for('admin.Index', filename = filename))


#app route for updating for uploading exam paper second time
@admin.route('/upload', methods=['POST','GET'])
def upload():
    if request.method == 'POST':
      files = request.files.getlist('examPaper[]')
      id_data = request.form['examID']
      for file in files:
        #updating exam paper name column 
        cur = mysql.connection.cursor()
        filename = secure_filename(file.filename)
        path = 'admin/'
        file.save(os.path.join(path, "static/uploads", filename))
        cur.execute("UPDATE examinations SET examPaperName=%s WHERE examID=%s", (filename, id_data))
        mysql.connection.commit()
        cur.close  
        

        
      flash('Exam Paper is successfully uploaded.')

    return redirect(url_for('admin.Index', filename = filename))





#app route for updating (for uploading an student namelist) - SQL done
@admin.route('/upload1', methods=['POST','GET'])
def upload1():
    global oldnumberofstudents, numberofstudents
    cur = mysql.connection.cursor()
    if request.method == 'POST':
      files = request.files.getlist('studentNamelist[]')
      id_data = request.form['examID']
      for file in files:
        filename = secure_filename(file.filename)
        path = 'admin/'
        file.save(os.path.join(path, "static/uploads", filename))
        cur.execute("UPDATE examinations SET studentNameList=%s WHERE examID=%s",(filename, id_data))
        mysql.connection.commit()
        cur.close

        #uploading namelist into MySQL student DATABASE
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + "/admin" + '/static/uploads/'
     
        cursor = mysql.connection.cursor()
        studentData = csv.reader(open(filepath + filename))
        pending = 'Pending'
        
        

        for row in studentData:
             studentname = (row[0])
             cursor.execute('INSERT INTO students (name, matric, email, username, password) VALUES (%s, %s, %s, %s, %s)', row)   
             cursor.execute('INSERT INTO statuses (examID, status) VALUES (%s, %s)', (id_data, pending)) 
             #updating status ID column
             cursor.execute("SELECT MAX(statusID) FROM statuses")
             lateststatusID = cursor.fetchone()
             cursor.execute('UPDATE statuses SET studentID = (SELECT studentID FROM students WHERE students.name = %s) WHERE statusID = %s' , (studentname, lateststatusID) )
        mysql.connection.commit()
        cursor.close

        
        

        #updating the examID of each student namelist 
        cursor2 = mysql.connection.cursor()
        valuezero = 0
        cursor2.execute('UPDATE students SET examID = %s WHERE examID = %s', (id_data, valuezero))
        mysql.connection.commit()
        cursor2.close
         
         
         
    return redirect(url_for('admin.Index'))

#app route for updating (for uploading an invigilator namelist) - SQL done
@admin.route('/upload2', methods=['POST','GET'])
def upload2():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
      files = request.files.getlist('invigilatorNamelist[]')
      id_data = request.form['examID']
      for file in files:
        filename = secure_filename(file.filename)
        path = 'admin/'
        file.save(os.path.join(path, "static/uploads", filename))
        cur.execute("""
               UPDATE examinations
               SET invigilatorNameList=%s
               WHERE examID=%s
            """,(filename, id_data))
        mysql.connection.commit()
        cur.close
        
        #uploading into MySQL DATABASE
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + "/admin" + '/static/uploads/'
     
        cursor = mysql.connection.cursor()
        invigilatorData = csv.reader(open(filepath + filename))
        for row in invigilatorData:
             cursor.execute('INSERT INTO invigilators (name, email, username, password, admin) VALUES (%s, %s, %s, %s, %s)', row)
        mysql.connection.commit()
        cursor.close

        #updating the examID of each student namelist 
        cursor2 = mysql.connection.cursor()
        valuezero = 0
        cursor2.execute('UPDATE invigilators SET examID = %s WHERE examID = %s', (id_data, valuezero))
        mysql.connection.commit()
        cursor2.close


    return redirect(url_for('admin.Index'))


#App route for deleting whole row of examination record - SQL done
@admin.route('/delete/<string:id_data>', methods=['POST','GET'])
def delete(id_data):
    flash("Examination Record Has Been Deleted Successfully.")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM examinations WHERE examID=%s", (id_data,))
    cur.execute("DELETE FROM students WHERE examID=%s", (id_data,))
    cur.execute("DELETE FROM statuses WHERE examID=%s", (id_data,))
    cur.execute("DELETE FROM invigilators WHERE examID=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('admin.Index'))

#App route for deleting exam paer  - SQL done
@admin.route('/deletepaper/<string:id_data>', methods=['POST','GET']) 
def deletepaper(id_data):
    cur = mysql.connection.cursor()
     
     
    cur.execute("UPDATE examinations SET examPaper = NULL WHERE examID=%s", [id_data])
    cur.execute("UPDATE examinations SET examPaperName = NULL WHERE examID=%s", [id_data])
    mysql.connection.commit()
    return redirect(url_for('admin.Index'))


#App route for deleting studentnamelist  - SQL done
@admin.route('/deletenamelist1/<string:id_data>', methods=['POST','GET']) 
def deletenamelist1(id_data):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE examID=%s", (id_data,))
    cur.execute("DELETE FROM statuses WHERE examID=%s", (id_data,))
    cur.execute("UPDATE examinations SET studentNameList = NULL WHERE examID=%s", (id_data, ))
    mysql.connection.commit()
    return redirect(url_for('admin.Index'))

#App route for deleting invigilator namelist  - SQL done
@admin.route('/deletenamelist2/<string:id_data>', methods=['POST','GET'])
def deletenamelist2(id_data):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM invigilators WHERE examID=%s", (id_data,))
    cur.execute("UPDATE examinations SET invigilatorNameList = NULL WHERE examID=%s", (id_data, ))
    mysql.connection.commit()
    return redirect(url_for('admin.Index'))

def write_file(data, filename):        
    with open(filename, 'wb') as file:
        file.write(data)

#app route for viewing exam paper PDF 
@admin.route('/view/<string:id_data>', methods=['POST','GET'])
def viewexam(id_data):        
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT examPaperName FROM examinations WHERE examID = %s', [id_data])
    examPaper = cur.fetchone() 
    print(examPaper)
    cur.close()
    

    #getting the name of the examPaper
    string1 = str(examPaper)
    print(string1)
    #remove first 17 characters
    string2 = string1[2:]
    print(string2)
    #remove last 25 characters
    string3 = string2[:-3]
    print(string3)
    # finalexamstring = string3.replace(" ", "_")
    # print(finalexamstring)
    
    

    filepath = '/admin/static/uploads/' + string3



    
    return render_template('viewfile.html', filepath = filepath)




#app route for viewing student namelist excel sheets - Modification Done
@admin.route('/viewnamelist1/<string:studentNamelist>', methods=['POST','GET'])
def viewnamelist1(studentNamelist):

    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + "/admin" + '/static/uploads/'
     

    return send_from_directory(filepath, studentNamelist)

#app route for viewing invigilator namelist excel sheets - Modification Done
@admin.route('/viewnamelist2/<string:invigilatorNamelist>', methods=['POST','GET'])
def viewnamelist2(invigilatorNamelist):

    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + "/admin" + '/static/uploads/'

    return send_from_directory(filepath, invigilatorNamelist)
    




