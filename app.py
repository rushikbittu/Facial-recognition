import face_recognition
import cv2
import os
from datetime import datetime
import numpy
from flask import Flask, request, render_template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__, template_folder="templates")

@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')

@app.route('/home', methods=['GET'])
def about():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def predict():
    print("[INFO] quantifying faces...")
    image_1 = face_recognition.load_image_file("path from data set")
    image_1_face_encoding = face_recognition.face_encodings(image_1)[0]

    image_2 = face_recognition.load_image_file(r"path from data set")
    image_2_face_encoding = face_recognition.face_encodings(image_2)[0]

    image_3 = face_recognition.load_image_file(r"path from data set")
    image_3_face_encoding = face_recognition.face_encodings(image_3)[0]

    image_4 = face_recognition.load_image_file(r"path from data set")
    image_4_face_encoding = face_recognition.face_encodings(image_4)[0]

    image_5 = face_recognition.load_image_file(r"path from data set")
    image_5_face_encoding = face_recognition.face_encodings(image_5)[0]

    known_face_encodings = [
        image_1_face_encoding,
        image_2_face_encoding,
        image_3_face_encoding,
        image_4_face_encoding,
        image_5_face_encoding,
        
    ]

    known_face_names = [
        "Names",
        "Names",
        "Names",
        "Names",
        "Names"
    ]

    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    print("[INFO] starting video stream...")
    video_capture = cv2.VideoCapture(0)

    recorded_faces = set()

    def log_attendance(name):
        with open('log.csv', mode="a") as logFile:
            pos = logFile.seek(0, os.SEEK_END)
            if pos == 0:
                logFile.write("Year,Month,Day,Time,Name,Attendance\n")
            ts = datetime.now()
            year, month, day = ts.strftime("%Y"), ts.strftime("%m"), ts.strftime("%d")
            time1 = ts.strftime("%H:%M:%S")
            info = f"{year},{month},{day},{time1},{name},Present\n"
            logFile.write(info)

    while True:
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = numpy.ascontiguousarray(small_frame[:, :, ::-1])

        if process_this_frame:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                if name not in recorded_faces:
                    log_attendance(name)
                    recorded_faces.add(name)
            face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    send_email()
    return render_template("upload.html")

def send_email():
    sender_email = "ftgyujklnbvcdserty@gmail.com"  
    receiver_email = "edrtyuikjhgf@gmail.com"
    password = "**********"  

    subject = "Attendance Log"
    body = "Please find the attached attendance log."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    filename = "log.csv"
    attachment = open(filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= " + filename)

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()

if __name__ == '__main__':
    app.run(debug=True)