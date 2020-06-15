import datetime, cv2, io, os, json, requests
from flask import Flask, Response
from kafka import KafkaConsumer
from PIL import Image

# Fire up the Kafka Consumer
topic = "distributed-video1"

consumer = KafkaConsumer(
    topic, 
    bootstrap_servers=['localhost:9092'])

# Set the consumer in a Flask App
app = Flask(__name__)

@app.route('/video', methods=['GET'])
def video():
    """
    This is the heart of our video display. Notice we set the mimetype to 
    multipart/x-mixed-replace. This tells Flask to replace any old images with 
    new values streaming through the pipeline.
    """
    return Response(get_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

def get_video_stream():
    """
    Here is where we recieve streamed images from the Kafka Server and convert 
    them to a Flask-readable format.
    """
    i=0
    for msg in consumer:
        bytes = msg.value
        image = Image.open(io.BytesIO(bytes))
        image.save("/home/little/Documents/Workflow_new/node_camera/camera_snapshots/"+str(i)+".jpg")
        i+=1
        yield (b'--frame\r\n' b'Content-Type: image/jpg\r\n\r\n' + msg.value + b'\r\n\r\n')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)
