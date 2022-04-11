from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
from main import mysql
import base64
import os
import cv2

from flask import Flask
import numpy as np
from flask_socketio import SocketIO, send
from flask_socketio import emit
from main import create_app
import face_recognition

student = Blueprint("student", __name__, template_folder = "templates", static_folder='static')

global selected_exam_id, submitted_id, submitted_face
submitted_id = 0
submitted_face = 0

global current_session_id, current_session_name
current_session_id = 0
current_session_name = "0"

camera = cv2.VideoCapture(0)

global camera_enabled 
camera_enabled = 1

######

saiful_image = face_recognition.load_image_file("student/saiful/saiful.jpg")
saiful_face_encoding = face_recognition.face_encodings(saiful_image)[0]

known_face_encodings = [
    saiful_face_encoding
]

known_face_names = [
    "Saiful"
]

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

######

@student.route('/pending/<session_id>', methods=['GET', 'POST'])
def pending(session_id):

    global current_session_id, current_session_name
    
    current_session_id = session_id
    print("global current_session_id: " + current_session_id)

    if session.get('id') is not None:
        print("session['id'] is present")
        print("session['id']: " + str(session['id']))
        print("session['name']: " + str(session['name']))
        current_session_name = session['name']
    else:       
        print("None")
        session['id'] = current_session_id
        session['name'] = current_session_name
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT \
        examinations.examID AS id, \
        examinations.courseName AS name, \
        examinations.courseCode AS code, \
        examinations.date AS date, \
        examinations.start AS start, \
        examinations.end AS end, \
        examinations.duration AS duration \
        FROM examinations \
        INNER JOIN statuses ON statuses.examID = examinations.examID WHERE statuses.status = 'pending' AND statuses.studentID = %s ", str(session['id']) )
    result = cur.fetchall()

    return render_template('pending.html', data = result, session_id = session['id'])

@student.route('/completed', methods=['GET', 'POST'])
def completed():

    cur = mysql.connection.cursor()
    cur.execute("SELECT \
        examinations.courseName AS name, \
        examinations.courseCode AS code, \
        examinations.date AS date, \
        examinations.start AS start, \
        examinations.end AS end, \
        examinations.duration AS duration \
        FROM examinations \
        INNER JOIN statuses ON statuses.examID = examinations.examID WHERE statuses.status = 'completed' AND statuses.studentID = %s ", str(session['id']) )
    result = cur.fetchall()

    return render_template('completed.html', data = result, session_id = session['id'])

@student.route('/expired', methods=['GET', 'POST'])
def expired():

    cur = mysql.connection.cursor()
    cur.execute("SELECT \
        examinations.courseName AS name, \
        examinations.courseCode AS code, \
        examinations.date AS date, \
        examinations.start AS start, \
        examinations.end AS end, \
        examinations.duration AS duration \
        FROM examinations \
        INNER JOIN statuses ON statuses.examID = examinations.examID WHERE statuses.status = 'expired' AND statuses.studentID = %s ", str(session['id']) )
    result = cur.fetchall()

    return render_template('expired.html', data = result, session_id = session['id'])

@student.route('/id_card/<exam_id>', methods = ['GET'])
def id_card(exam_id):
    global selected_exam_id

    selected_exam_id = exam_id

    return render_template('id_card.html')

@student.route('/receive_id', methods=['POST'])
def receive_id():
    global submitted_id, current_session_id

    session['id'] = current_session_id
    
    data = request.form["img"]      
    binary_image = base64.b64decode(data)       # Convert base64 to binary

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM idimages WHERE studentID = %s', str(session['id']))
    student = cursor.fetchone()
    cursor.close()

    cur = mysql.connection.cursor()

    if student:
        sql = "UPDATE idimages set image = %s  WHERE studentID = %s"
        cur.execute(sql, (binary_image, str(session['id'])))

    else:
        sql = "INSERT INTO idimages (studentID, image) VALUES (%s, %s)"
        cur.execute(sql, (str(session['id']), binary_image))

    mysql.connection.commit()

    submitted_id = 1

    response = jsonify("ID OK!")

    return response

@student.route('/face', methods=['POST','GET'])
def face():
    global submitted_id, selected_exam_id

    if submitted_id == 1:
        submitted_id = 0
        
        flash('Identity card captured successfully')
        
        return render_template('face.html')
    
    else:
        flash('You must capture your identity card to proceed','id_error')
        
        return render_template('id_card.html')

@student.route('/receive_face', methods=['POST'])
def receive_face():
    global submitted_face, current_session_id

    session['id'] = current_session_id

    data = request.form["img"]      
    binary_image = base64.b64decode(data)       # Convert base64 to binary

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM faceimages WHERE studentID = %s', str(session['id']))
    student = cursor.fetchone()
    cursor.close()

    cur = mysql.connection.cursor()

    if student:
        sql = "UPDATE faceimages set image = %s  WHERE studentID = %s"
        cur.execute(sql, (binary_image, str(session['id'])))

    else:
        sql = "INSERT INTO faceimages (studentID, image) VALUES (%s, %s)"
        cur.execute(sql, (str(session['id']), binary_image))

    mysql.connection.commit()

    submitted_face = 1

    response = jsonify("FACE OK!")

    return response

@student.route('/instruction', methods=['POST','GET'])
def instruction():
    global submitted_face

    if submitted_face == 1:
        submitted_face = 0

        flash('Face captured successfully')

        return render_template('instruction.html')

    else:

        flash('You must capture your face to proceed','face_error')

        return render_template('face.html')

def write_file(data, filename):         
    with open(filename, 'wb') as file:
        file.write(data)

@student.route('/exam', methods=['POST','GET'])
def exam():
    global selected_exam_id, current_session_id, camera_enabled, camera

    print(camera_enabled)
    if camera_enabled == 0:                 
        camera = cv2.VideoCapture(0)    # Reopen webcam 
        camera_enabled = 1              # Set webcam flag
    
    print(camera_enabled)

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM examinations WHERE examID = %s', (selected_exam_id, ))
    data = cur.fetchone()
    cur.close()
    
    write_file(data[7], "student\static\exam.pdf")

    duration = data[6]*3600     # Convert hours(float) to seconds

    #socketio.emit('test_response', {'data': 'Test response sent'})

    return render_template('exam.html', num = duration, session_id = current_session_id)

@student.route('/upload_page', methods=['POST','GET'])
def upload_page():

    global camera_enabled, current_session_id, current_session_name

    # NEED FOR REINITIALISATION OF SESSION PARAMETERS IN THE EVENT OR TIMES UP AND AUTO DIRECT TO UPLOAD PAGE(JAVASCRIPT FUNCTION DOES NOT HAVE ANY SESSION DATA)
    session['id'] = current_session_id          
    session['name'] = current_session_name

    print(camera_enabled)
    if camera_enabled == 1:
        camera.release()        # Close webcam 
        camera_enabled = 0      # Unset webcam flag

    print(camera_enabled)
    
    if os.path.exists('student\static\exam.pdf') == True:
        os.remove("student\static\exam.pdf")

    return render_template('upload.html', session_id = current_session_id) # Need to pass session to the upload page which then passes the session id to pending function 

@student.route('/upload', methods=['POST'])
def upload():
    global selected_exam_id, current_session_id

    session['id'] = current_session_id
    
    if request.method == "POST":

        files = request.files.getlist('files[]')

        for file in files: 
            if file.filename == '':
                flash('Please select file(s) to upload', 'error')   # Filter flash messages by the term 'error'
                return redirect(url_for('student.upload_page'))

            elif file and not allowed_file(file.filename):
                flash('Only images (png/jpg) are allowed','error')
                return redirect(url_for('student.upload_page'))

            elif file and allowed_file(file.filename):

                blob_file = file.read()
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO scripts (studentID, examID, script) VALUES (%s, %s, %s)", (str(session['id']), selected_exam_id, blob_file))
                mysql.connection.commit()

        flash('File(s) successfully uploaded')
    
        return redirect(url_for('student.upload_page'))

ALLOWED_EXTENSIONS = set(['png', 'jpg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_frames():
    while True:
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@student.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@student.route('/update_status/<session_id>')
def update_status(session_id):

    global selected_exam_id

    cur = mysql.connection.cursor()
    sql = "UPDATE statuses SET status = 'completed' WHERE studentID = %s AND examID = %s"
    cur.execute(sql, (session_id, selected_exam_id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('student.pending', session_id = session_id))






#####
def generate_detection():  

    import mysql.connector

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="fyp"
    )
    mycursor = mydb.cursor()
    while True:
        success, frame = camera.read() 
        if not success:
            break
        else:  
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                if matches != [True]:
                    print("Unknown face detected")
                    #socketio.emit('test_response', {'data': ["Unknown face detected"]})
                    
                    import time

                    dt_string= time.strftime('%Y-%m-%d %H:%M:%S')
                    mycursor = mydb.cursor()
                    sql = "INSERT INTO studenterror (studentID, studentName,  timeOfError , errorDetail) VALUES (%s, %s, %s, %s)"
                    val  = ("1", "1",dt_string, str(name))
                    mycursor.execute(sql,val )
                    mydb.commit()
                   
        
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    print(name)

                face_names.append(name)
                
                #socketio.emit('test_response', {'data': face_names})

                y  = len(face_names)
                if y > 1:
                    #print("Multple faces detected")
                    print(face_names)
                    
                    import time
                    dt_string= time.strftime('%Y-%m-%d %H:%M:%S')
                    mycursor = mydb.cursor()
                    sql = "INSERT INTO studenterror (studentID, studentName,  timeOfError , errorDetail) VALUES (%s, %s, %s, %s)"
                    val  = ("1", "1",dt_string, str(face_names))
                    mycursor.execute(sql,val )
                    mydb.commit()
            
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@student.route('/detection')
def detection():
    return Response(generate_detection(),mimetype='multipart/x-mixed-replace; boundary=frame')

