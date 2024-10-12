# Import necessary libraries
import numpy as np
import tensorflow as tf
from keras.models import model_from_json
from keras.saving import register_keras_serializable
from flask import Flask, request, jsonify
import json
import psycopg2  # Add this to interact with PostgreSQL



# Register the custom huber_loss function
@register_keras_serializable()
def huber_loss(y_true, y_pred, clip_value=1):
    assert clip_value > 0.
    
    x = y_true - y_pred
    if np.isinf(clip_value):
        return .5 * tf.square(x)
    
    condition = tf.abs(x) < clip_value
    squared_loss = .5 * tf.square(x)
    linear_loss = clip_value * (tf.abs(x) - .5 * clip_value)
    
    return tf.where(condition, squared_loss, linear_loss)

# Load the model architecture from JSON file
with open("./models/DDQN_model.json", "r") as json_file:
    model = model_from_json(json.load(json_file))

# Load the model weights
model.load_weights("./models/DDQN_model.weights.h5")

# Compile the model with the custom huber_loss function
model.compile(loss=huber_loss, optimizer="sgd")

# Initialize Flask app
app = Flask(__name__)

# Define a dictionary for label mapping (make sure this is loaded from your saved file)
label_dict = {
    '0': 'Benign',
    '1': 'Botnet',
    '2': 'Brute-force',
    '3': 'DDoS attack',
    '4': 'DoS attack',
    '5': 'Infilteration',
    '6': 'Web attack'
}

# Database connection setup (you can load environment variables here if needed)
def get_db_connection():
    conn = psycopg2.connect(
        host="db",  # the service name from docker-compose
        database="mydatabase",
        user="user",
        password="password"
    )
    return conn

def create_predictions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            predicted_class INTEGER,
            class_label VARCHAR(255)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Route for predictions
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input data from request
        data = request.json
        input_data = np.array(data['input']).reshape(1, -1)  # Reshape as per the model requirements
        
        # Predict using the loaded model
        prediction = model.predict(input_data)
        predicted_class = np.argmax(prediction, axis=1)
        
        # Prepare the response
        response = {
            'predicted_class': int(predicted_class[0]),
            'class_label': label_dict[str(predicted_class[0])]
        }

        # Store a value in the database (for example, store the predicted class and class_label)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (predicted_class, class_label) VALUES (%s, %s)",
            (int(predicted_class[0]), label_dict[str(predicted_class[0])])
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Flask route for checking server status
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Server is running"}), 200

# Run the app
if __name__ == '__main__':
    create_predictions_table()  # Ensure the table is created when the app starts
    app.run(host='0.0.0.0', port=5001)
