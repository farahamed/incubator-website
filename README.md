# incubator-website
Infant Incubator Monitoring System
A real-time IoT web application designed to monitor infant health parameters within an incubator. The system integrates hardware (Arduino/Sensors) with a web dashboard to track temperature, heart rate, humidity, sound, light, and weight.

Features
Real-time Dashboard: Uses WebSockets (Flask-SocketIO) to stream live sensor data from the hardware to the browser without refreshing.

User Management: Secure Signup and Login system for medical staff.

Infant Registration: Register and manage infant profiles, linking them to specific incubators.

Data Logging: Automatically logs all incoming sensor data into a InfantData.csv file for historical analysis.

Database Integration: Powered by PostgreSQL (hosted on Neon/Azure) to store user and patient records.

Hardware Connectivity: Interface with Arduino via Serial Communication (PySerial).

Tech Stack
Backend: Python (Flask)

Real-time Communication: Flask-SocketIO

Database: PostgreSQL (psycopg2)

Hardware Interface: PySerial

Frontend: HTML5, CSS3, JavaScript (Jinja2 Templates)

Prerequisites
Before running the application, ensure you have the following installed:

Python 3.8+

PostgreSQL (Local or Cloud instance)

Arduino IDE (To upload the sensor code to your hardware)
