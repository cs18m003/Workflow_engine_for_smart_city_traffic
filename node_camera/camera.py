from datetime import datetime
from flask import render_template
from node_camera import app
from flask import Flask, redirect, url_for, request, render_template, Response
from flask import Flask, request, jsonify, render_template
import pandas as pd
import requests
import os, sys
from importlib import import_module
import pyodbc

cam_dir = '/home/little/Documents/Workflow_new/node_camera/camera_snapshots/'

# starts zookeeper
@app.route('/traffic_handle/start_zookeeper', methods=['GET'])
def zookeeper():
    os.system('cd && cd Kafka && sudo bin/zookeeper-server-start.sh config/zookeeper.properties')
    return 'success'

# starts kafka-server
@app.route('/traffic_handle/start_kafka', methods=['GET'])
def kafka():
    os.system('cd && cd Kafka && sudo bin/kafka-server-start.sh config/server.properties')
    return 'success'

# stops kafka-server
@app.route('/traffic_handle/stop_kafka', methods=['GET'])
def kafka_stop():
    os.system('cd && cd Kafka && sudo bin/kafka-server-stop.sh config/server.properties')
    return 'success'

# stops zookeeper
@app.route('/traffic_handle/stop_zookeeper', methods=['GET'])
def zookeeper_stop():
    os.system('cd && cd Kafka && sudo bin/zookeeper-server-stop.sh config/zookeeper.properties')
    return 'success'

#node camera
@app.route('/node_camera')
def GetImagePath():
    i=0
    listing = os.listdir(cam_dir)
    for file in listing:
        #print(len(file))
        #url = 'http://localhost:5000/wfe/wf/submit'
        node_url = 'http://localhost:5000/wfe/node/submit'
        data={'img_path':cam_dir+file,
                'count_cars':0
                }
        myobj = {'jobid': i, 
                 'nodeid':'node_camera',
                 'wfid':'wf_traffic',
                 'nstatus':'pending',
                 'data':{'img_path':cam_dir+file,
                         'count_cars':0
                        }
                 }
        #myobj = {'jobid': i, 
        #         'nodeid':'node_camera',
        #         'wfid':'wf_traffic',
        #         'nstatus':'pending',
        #         'img_path':cam_dir+file,
        #         'count_cars':0
        #         }
        #response=requests.post(url, json=myobj)
        #print('response',response)
        response1=requests.post(node_url, json=myobj)
        print('response',response1)
        try :
            conn = pyodbc.connect("Driver={MySQL ODBC 8.0 Unicode Driver};"
                  "server=localhost;"
                  "database=DbTest;"
                  "user=workflow;"
                  "password=password;"
                  "Trusted_Connection=yes;")
            cursor = conn.cursor() 
            #SQLCommand = ('INSERT INTO node_node (jobid,nodeid,wfid,nstatus,img_path,CarCount) VALUES (?,?,?,?,?,?);')
            SQLCommand = ('INSERT INTO node (jobid,nodeid,wfid,nstatus,data) VALUES (?,?,?,?,?);')
            #values = [i,'node_camera','wf_traffic','pending',cam_dir+file,0]
            values = [i,'node_camera','wf_traffic','pending',str(data)]
            cursor.execute(SQLCommand,values)
            conn.commit()
            conn.close()
        except :
            pass
        i=i+1
        print('database inserted')
        #break
    return 'Images Loaded'


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )