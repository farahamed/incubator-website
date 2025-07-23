from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
from psycopg2.extras import DictCursor
from werkzeug.utils import secure_filename
import os
import serial.tools.list_ports
from flask_socketio import SocketIO
import serial
import time
import threading

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://your_username:your_password@localhost/your_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

########################################################################################################################
########################################################################################################################

def connect_db():
    conn = psycopg2.connect(
        dbname="Infant_Incubator",
        user="Infant_Incubator_owner",
        password="npg_iVeHgj21UAGF",
        host="ep-icy-leaf-a9v7qpwh-pooler.gwc.azure.neon.tech",
        port="5432"
    )
    return conn

########################################################################################################################
########################################################################################################################
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

########################################################################################################################
########################################################################################################################

@app.route('/contactus')
def contactus():
    return render_template('Contact.html')

########################################################################################################################
########################################################################################################################
@app.route("/infantdata")
def infantdata():
    return render_template("InfantData.html")

########################################################################################################################
########################################################################################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        key = request.form.get('username')
        password = request.form.get('password')
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=DictCursor)

        cursor.execute("SELECT * FROM users WHERE username=%(username)s AND password=%(password)s", {"username": key, "password": password})
        conn.commit()
        result = cursor.fetchone()
        if result:
            return redirect(url_for('infantdata',username=key))
        else:
            return "Invalid credentials!", 401

########################################################################################################################
########################################################################################################################
@app.route('/signup')
def signup():
   return render_template('Signup.html')

########################################################################################################################
########################################################################################################################
@app.route('/submit_User',methods=['GET', 'POST'])
def submit_user():
    conn = connect_db()
    if request.method == 'GET':
        return render_template('Signup.html')

    if request.method == 'POST':
        email=request.form.get('email')
        name=request.form.get('name')
        role=request.form.get('role')
        username=request.form.get('username')
        password=request.form.get('password')
        userid=request.form.get('userid')
        phonenumber=request.form.get('phonenumber')

        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(' INSERT INTO users(email,name,role,username,password,user_id,phone)values (%s,%s,%s,%s,%s,%s,%s)',
            (email,name,role,username,password,userid,phonenumber))
        conn.commit()
        return redirect('/signup')

########################################################################################################################
########################################################################################################################
@app.route('/registration')
def registration():
    return render_template('registration.html')

########################################################################################################################
########################################################################################################################
@app.route('/submit_registration',methods=['GET', 'POST'])
def submit_registration():
    conn=connect_db()
    if request.method == 'GET':
         return render_template('registration.html')

    if request.method == 'POST':
        infant_id=request.form.get('infant_id') #
        full_name=request.form.get('full_name') #
        age = request.form.get('age') #
        birth_date = request.form.get('birth_date')#
        weight_kg=request.form.get('weight_kg') #
        incubator_number=request.form.get('incubator_number') #
        assigned_user=request.form.get('assigned_user') #

        cur=conn.cursor()
        cur.execute('INSERT INTO infants(infant_id,full_name,age,birth_date,weight_kg,incubator_number,assigned_user) values (%s,%s,%s,%s,%s,%s,%s)',
            (infant_id,full_name,age,birth_date,weight_kg,incubator_number,assigned_user))
        conn.commit()

        return redirect('/registration')

########################################################################################################################
########################################################################################################################
socketio = SocketIO(app, cors_allowed_origins="*")

ARDUINO_PORT = "COM5"  # Update as needed
BAUD_RATE = 9600
FILE_NAME = "InfantData.csv"

try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2)
    print(f"Connected to Arduino on {ARDUINO_PORT}")

except serial.SerialException as e:
    print(f"Error: {e}")
    ser = None

# CSV file Headers
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w") as file:
        file.write("Temperature,Heart Rate,Humidity,Sound Level,Light Level,Weight\n")

# Function to Read, Log to CSV, and Send Serial Data
def read_log_send_serial():
    global ser
    while True:
        if ser:
            try:
                line = ser.readline().decode("utf-8").strip()
                if line:
                    print(f"Received: {line}")  # Log data to console

                    # Format: "temp,heart_rate,humidity,sound,light,weight"
                    data_values = line.split(",")

                    if len(data_values) == 6:
                        sensor_data = {
                            "temp": data_values[0],
                            "heart_rate": data_values[1],
                            "humidity": data_values[2],
                            "sound_level": data_values[3],
                            "light_level": data_values[4],
                            "weight": data_values[5],
                        }

                        # Send data to UI
                        socketio.emit("sensor_data", sensor_data)

                        # Append data to CSV file
                        with open(FILE_NAME, "a") as file:
                            file.write(",".join(data_values) + "\n")

            except (serial.SerialException, UnicodeDecodeError) as e:
                print(f"Serial Read Error: {e}")
                break  # Exit loop if error occurs

        time.sleep(1)

# Start Serial Reading & Logging in Background Thread
threading.Thread(target=read_log_send_serial, daemon=True).start()

########################################################################################################################
########################################################################################################################

# Run Flask App
if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)