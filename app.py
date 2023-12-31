from __future__ import division, print_function
#import sys
import os
import cv2
#import re
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from keras.models import model_from_json
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import statistics as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
from dotenv import dotenv_values
env_vars=dotenv_values()

app = Flask(__name__)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=env_vars['client_id'],
                                               client_secret=env_vars['client_secret'],
                                               redirect_uri='http://localhost:5000/callback',
                                               scope='user-library-read'))

@app.route("/")
def home():
    print("getting")
    return render_template("index1.html")

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp.auth_manager.get_access_token(code)
    access_token = token_info['access_token']
    sp.set_auth(access_token)


@app.route('/happy-songs' , methods = ['GET', 'POST'])
def get_happy_songs():
    results = sp.search(q='entertaining telugu songs', type='track', limit=50)
    happy_songs = []
    for track in results['tracks']['items']:
        song_name = track['name']
        artist_name = track['artists'][0]['name']
        song_url = track['external_urls']['spotify']
        image_url = track['album']['images'][0]['url']
        happy_songs.append({
            'song_name': song_name,
            'artist_name': artist_name,
            'song_url': song_url,
            'image_url': image_url
        })
        random.shuffle(happy_songs)
    return render_template("happy_songs.html",happy_songs=happy_songs)
    
@app.route('/camera', methods = ['GET', 'POST'])
def camera():
    i=0

    GR_dict={0:(0,255,0),1:(0,0,255)}
    emotion_dict = {0: "angry", 1: "disgust", 2: "fear", 3: "happy", 4: "neutral", 5: "sad", 6: "surprise"}
    # load json and create model
    json_file = open('model/emotion_model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    emotion_model = model_from_json(loaded_model_json)
    # load weights into new model
    emotion_model.load_weights("model/emotion_model.h5")

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    output=[]
    cap = cv2.VideoCapture(0)
    while (i<=30):
        # ret, img = cap.read()
        # faces = face_cascade.detectMultiScale(img,1.05,5)

        # for x,y,w,h in faces:

        #     face_img = img[y:y+h,x:x+w] 

        #     resized = cv2.resize(face_img,(224,224))
        #     reshaped=resized.reshape(1, 224,224,3)/255
        #     predictions = emotion_model.predict(reshaped)

        #     max_index = np.argmax(predictions[0])

        #     emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'neutral', 'surprise')
        #     predicted_emotion = emotions[max_index]
        #     output.append(predicted_emotion)
            
            
            
        #     cv2.rectangle(img,(x,y),(x+w,y+h),GR_dict[1],2)
        #     cv2.rectangle(img,(x,y-40),(x+w,y),GR_dict[1],-1)
        #     cv2.putText(img, predicted_emotion, (x, y-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2)

            # Find haar cascade to draw bounding box around face
        ret, frame = cap.read()
        frame = cv2.resize(frame, (1280, 720))
        if not ret:
            break
        face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect faces available on camera
        num_faces = face_detector.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)

        # take each face available on the camera and Preprocess it
        for (x, y, w, h) in num_faces:
            cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (0, 255, 0), 4)
            roi_gray_frame = gray_frame[y:y + h, x:x + w]
            cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)

            # predict the emotions
            emotion_prediction = emotion_model.predict(cropped_img)
            maxindex = int(np.argmax(emotion_prediction))
            output.append(emotion_dict[maxindex])
            cv2.putText(frame, emotion_dict[maxindex], (x+5, y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            i = i+1

        cv2.imshow('LIVE', frame)
        key = cv2.waitKey(1)
        if key == 27: 
            cap.release()
            cv2.destroyAllWindows()
            break
    print(output)
    cap.release()
    cv2.destroyAllWindows()
    final_output1 = st.mode(output)
    return render_template("buttons.html",final_output=final_output1)


@app.route('/templates/buttons', methods = ['GET','POST'])
def buttons():
    return render_template("buttons.html")

@app.route('/movies/surprise', methods = ['GET', 'POST'])
def moviesSurprise():
    return render_template("moviesSurprise.html")

@app.route('/movies/angry', methods = ['GET', 'POST'])
def moviesAngry():
    return render_template("moviesAngry.html")

@app.route('/movies/sad', methods = ['GET', 'POST'])
def moviesSad():
    return render_template("moviesSad.html")

@app.route('/movies/disgust', methods = ['GET', 'POST'])
def moviesDisgust():
    return render_template("moviesDisgust.html")

@app.route('/movies/happy', methods = ['GET', 'POST'])
def moviesHappy():
    return render_template("moviesHappy.html")

@app.route('/movies/fear', methods = ['GET', 'POST'])
def moviesFear():
    return render_template("moviesFear.html")

@app.route('/movies/neutral', methods = ['GET', 'POST'])
def moviesNeutral():
    return render_template("moviesNeutral.html")

@app.route('/songs/surprise', methods = ['GET', 'POST'])
def songsSurprise():
    return render_template("songsSurprise.html")

@app.route('/songs/angry', methods = ['GET', 'POST'])
def songsAngry():
    return render_template("songsAngry.html")

@app.route('/songs/sad', methods = ['GET', 'POST'])
def songsSad():
    return render_template("songsSad.html")

@app.route('/songs/disgust', methods = ['GET', 'POST'])
def songsDisgust():
    return render_template("songsDisgust.html")

@app.route('/songs/happy', methods = ['GET', 'POST'])
def songsHappy():
    return render_template("songsHappy.html")

@app.route('/songs/fear', methods = ['GET', 'POST'])
def songsFear():
    return render_template("songsFear.html")

@app.route('/songs/neutral', methods = ['GET', 'POST'])
def songsNeutral():
    return render_template("songsSad.html")

@app.route('/templates/join_page', methods = ['GET', 'POST'])
def join():
    return render_template("join_page.html")
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)