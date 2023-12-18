from flask import Flask, render_template, Response
import cv2
import numpy as np
import pickle
import pandas as pd
from ultralytics import YOLO
import cvzone
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
with open("recorded_polylines", "rb") as f:
    data = pickle.load(f)
    polylines, area_names = data['polylines'], data['area_names']

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")

model = YOLO('yolov8s.pt')
cap = cv2.VideoCapture('easy1.mp4')


def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (1020, 500))
        frame_copy = frame.copy()
        results = model.predict(frame)
        a = results[0].boxes.data
        px = pd.DataFrame(a).astype("float")
        list1 = []
        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])

            c = class_list[d]
            cx = int(x1 + x2) // 2
            cy = int(y1 + y2) // 2
            if 'car' in c:
                list1.append([cx, cy])

        counter1 = []
        for i, polyline in enumerate(polylines):
            for i1 in list1:
                cx1 = i1[0]
                cy1 = i1[1]
                result = cv2.pointPolygonTest(polyline, ((cx1, cy1)), False)
                if result >= 0:
                    cv2.circle(frame, (cx1, cy1), 5, (255, 0, 0), -1)
                    cv2.polylines(frame, [polyline], True, (0, 0, 255), 2)
                    counter1.append(cx1)

        car_count = len(counter1)
        free_space = len(polylines) - car_count

        cvzone.putTextRect(frame, f'CAR Counter:-{car_count}', (50, 60), 2, 2)
        cvzone.putTextRect(frame, f'Free Space:-{free_space}', (50, 160), 2, 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == "__main__":
    app.run(debug=True)
