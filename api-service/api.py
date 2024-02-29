# Machine learning service
from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Setup API and ENV
app = Flask(__name__)
CORS(app)
load_dotenv("tokens.env")

# Home page
@app.route('/')

# Home endpoint of API
def index():
    return 'Hello, World!'

# Load Machine Learning Model
with open("/usr/src/app/14-feature-model.pkl", "rb") as f:
     clf = pickle.load(f)

def predict_grade(input,clf=clf):
    pred = 100 * (clf.predict(input) / 20) # Turn prediction into percentage
    pred = np.round(pred,2)
    if pred > 100: # If pred is over 100% return 100% only
      return 100
    else:
      return list(pred)

def format_data_for_pred(data):
    feature_order = ['age', 'Medu', 'Fedu', 'failures', 'goout', 'absences', 'G1', 'G2','Mjob_other', 'Fjob_teacher', 'schoolsup_yes', 'studytime','internet_yes', 'traveltime']
    input = []
    for attribute in feature_order:
       val = int(data.get(attribute))
       # Process input values into the required format for model
       if attribute == "absences":
          if val > 96:
             val = 96
       if attribute == "failures": #(numeric: n if 1<=n<3, else 4)
          if val >= 4:
             val = 4
       if attribute == "studytime": #(numeric: 1 - <2 hours, 2 - 2 to 5 hours, 3 - 5 to 10 hours, or 4 - >10 hours)
          if val > 10:
             val = 4
          elif val >= 5:
             val = 3
          elif val >= 2:
             val = 2
          else: 
             val = 1
       if attribute == "traveltime": #(numeric: 1 - <15 min., 2 - 15 to 30 min., 3 - 30 min. to 1 hour, or 4 - >1 hour)
          if val > 60: # recieved in minutes
             val = 4
          elif val >=30:
             val = 3
          elif val >=15:
             val = 2
          else:
             val = 1
       print("val-type: {}, val: {}".format(type(val), val))
       input.append(val)
    # Convert Percents back into out of 20
    input[feature_order.index("G1")] = input[feature_order.index("G1")]/100 * 20
    input[feature_order.index("G2")] = input[feature_order.index("G2")]/100 * 20
    return np.array(input).reshape(1,-1)

# Verify request
def verify(req_auth_token):
    # Load accepted authorization tokens
    if req_auth_token in os.getenv("AUTH").split(","):
       return
    else:
       print("Invalid Authorization Token")
       raise ValueError("Invalid Authorization Token")

# Requests come from student portal on website
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json() # Unpack data
    # Verify request
    verify(data['auth_token'])
    input = format_data_for_pred(data) # Reformat data
    prediction = predict_grade(input) # Predict with model
    return jsonify({'prediction':prediction})

# Requests come from google form
@app.route("/googleform", methods=["POST"])
def recieve():
    data = request.get_json() # Unpack data
    # Verify request
    verify(data['auth_token'])

    mydb = mysql.connector.connect(
      host = "db",
      user = "exampleuser",
      passwd = "examplepass",
      database = "exampledb"
    )

    cursor = mydb.cursor()

    # Table layout for faculty_portal_students   
    """
    CREATE TABLE faculty_portal_students (
    studentId INT AUTO_INCREMENT PRIMARY KEY,
    First_name VARCHAR(50) NOT NULL,
    Last_name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    Fedu INT NOT NULL,
    Fjob_teacher INT NOT NULL,
    Medu INT NOT NULL,
    Mjob_other INT NOT NULL,
    goout INT NOT NULL,
    internet_yes INT NOT NULL,
    studytime INT NOT NULL,
    traveltime INT NOT NULL,
    absences INT NOT NULL,
    schoolsup_yes INT NOT NULL,
    G1 FLOAT NOT NULL,
    G2 FLOAT NOT NULL,
    predicted_G3 FLOAT NOT NULL);
    """

    # Predict G3 and store it
    input = format_data_for_pred(data) # Reformat data
    predicted_G3 = predict_grade(input) # Predict with model
    # Construct the SQL INSERT statement
    sql = """
    INSERT INTO faculty_portal_students (First_name, Last_name, Email, age, Fedu, Fjob_teacher, Medu, Mjob_other, goout, internet_yes, studytime, traveltime, absences, failures, schoolsup_yes, G1, G2, predicted_G3)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Execute the INSERT statement with the form data and predicted grade
    cursor.execute(sql, (data["First_name"], data["Last_name"], data["Email"], data["age"], data["Fedu"], data["Fjob_teacher"], data["Medu"], data["Mjob_other"], data["goout"], data["internet_yes"], data["studytime"], data["traveltime"], data["absences"], data["failures"], data["schoolsup_yes"], data["G1"], data["G2"], float(predicted_G3[0])))

    # Commit changes to the DB
    mydb.commit()

    return jsonify({'message': str(data)})

# API Stuff
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
