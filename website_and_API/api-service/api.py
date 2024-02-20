# Machine learning service
from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
from flask_cors import CORS
# Setup API
app = Flask(__name__)
CORS(app)
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

@app.route('/predict', methods=['POST'])
def predict():
    print("PREDICTING G3")
    data = request.get_json() # Unpack data
    print(type(data))
    print('data:', data)
    input = format_data_for_pred(data) # Reformat data
    prediction = predict_grade(input) # Predict with model
    return jsonify({'prediction':prediction})


# API Stuff
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
