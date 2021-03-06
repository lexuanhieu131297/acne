import os
import sys

# Flask
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
from keras.applications.vgg16 import preprocess_input, decode_predictions
from keras.models import load_model
from tensorflow.keras.preprocessing import image
from keras_efficientnets import EfficientNetB4
from keras_efficientnets import custom_objects
from keras.utils.data_utils import get_file

# Some utilites
import numpy as np
from util import base64_to_pil

# Declare a flask app
app = Flask(__name__)


# You can use pretrained model from Keras
# Check https://keras.io/applications/


# Model saved with Keras model.save()
MODEL_PATH = 'https://www.dropbox.com/s/w9w2p8jurfk9vqn/acne_model.h5?dl=1'

# Load your own trained model
print('Prepare to load')
h5_path = get_file('model.h5',MODEL_PATH)
model = load_model(h5_path,compile=False)
model._make_predict_function()          # Necessary
print('Model loaded. Start serving...')


def model_predict(img, model):
    img = img.resize((380, 380))
    
    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    x = np.expand_dims(x, axis=0)

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
    x = preprocess_input(x, mode='tf')

    preds = model.predict(x)
    return preds


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the image from post request
        img = base64_to_pil(request.json)
        dict_id=['mild', 'intermediate', 'upper intermediate', 'extreme']
        # Save the image to ./uploads
        # img.save("./uploads/image.png")

        # Make prediction
        preds = model_predict(img, model)

        # Process your result for human
        pred_proba = int(np.argmax(preds))       # Max probability
        # print(pred_proba)
        # pred_class = decode_predictions(preds, top=1)   # ImageNet Decode

        # result = str(pred_class[0][0][1])               # Convert to string
        # result = result.replace('_', ' ').capitalize()
        result=dict_id[pred_proba]
        # Serialize the result, you can add additional fields
        return jsonify(result=result, probability=pred_proba)
        
    return None


if __name__ == '__main__':
    # app.run(port=5002, threaded=False)

    # Serve the app with gevent
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()

