from datetime import datetime
from flask import render_template
from node_analytics import app
import cv2
import pyodbc
import time
from time import sleep
car_cascade = cv2.CascadeClassifier('/home/little/Documents/Workflow_new/node_analytics/cars.xml')

@app.route('/node_analytics')
def GetImagePath():
    #while True:
    for i in range(10):
        conn1 = pyodbc.connect("Driver={MySQL ODBC 8.0 Unicode Driver};"
                  "server=localhost;"
                  "database=DbTest;"
                  "user=workflow;"
                  "password=password;"
                  "Trusted_Connection=yes;")
        cursor1 = conn1.cursor() 
        conn2 = pyodbc.connect("Driver={MySQL ODBC 8.0 Unicode Driver};"
                  "server=localhost;"
                  "database=DbTest;"
                  "user=workflow;"
                  "password=password;"
                  "Trusted_Connection=yes;")
        cursor2 = conn2.cursor() 
    
        print ('Processing workflow')
        cursor1.execute('select  * from node where nodeid=\'node_analytics\' and nstatus=\'pending\'')
        print('WF processing...')
        for row in cursor1:    
            jobid=row[0]
            nodeid=row[1]
            wfid=row[2]
            nstatus = row[3] 
            local_data=eval(row[4])
            img_path = local_data['img_path']
            #img_path=row[4]
            CarCount = local_data['count_cars']
            #CarCount = row[5] 
            print(jobid,nodeid)
            image = cv2.imread(img_path)
            grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cars = car_cascade.detectMultiScale(grayImage)
            if len(cars) == 0:
                    CarCount = 1
                    print('Cars are')
                    print('hello')
                    print(CarCount)
            else:
                for (x,y,w,h) in cars:
                    cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),1)
                cv2.rectangle(image, ((0,image.shape[0] -25)),(270, image.shape[0]), (255,255,255), -1)
                cv2.putText(image, "Number of cars detected: " + str(cars.shape[0]), (0,image.shape[0] -10), cv2.FONT_HERSHEY_TRIPLEX, 0.5,  (0,0,0), 1)
     
                CarCount = cars.shape[0] 
                print('cars are')
                print('hello1')
                print(CarCount)
        
            q1 = 'DELETE FROM node WHERE jobid=?'
            cursor1.execute(q1,(jobid,))
        
            insert_data={'img_path':local_data['img_path'],
                         'count_cars':CarCount
                        }
            q2 = ('INSERT INTO node (jobid,nodeid,wfid,nstatus,data) values (?,?,?,?,?);')
            values = [jobid,nodeid,wfid,nstatus,str(insert_data)]
            cursor1.execute(q2,values)
            break
            # end for loop
        cursor1.commit()
        cursor2.commit()
        conn1.close()
        conn2.close()
        #i=i+1
    return 'analysis done'

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
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

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
