"""
Routes and views for the flask application.
"""
import pyodbc
from datetime import datetime
from flask import render_template
from process_wf import app
from time import sleep

'''def process_message(nodeid,wfid,mydata) :
    print ('conditional routing happens here... mydata',mydata)
    return 'ny', mydata'''

def process_message(nodeid,CarCount) :
    print ('conditional routing happens here... mydata')
    if(nodeid=='node_camera'):
        return 'node_analytics'
    if(nodeid=='node_analytics' and CarCount<10):
        return 'node_ignore'
    if(nodeid=='node_analytics' and CarCount>=10):
        return 'node_PCR'

#engine infinite loop
@app.route('/process_workflow')
def process_wf():
    #while True :
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
        sleep(3) #sleep for one sec
        print ('Processing workflow')
        qstr = "SELECT * FROM wf WHERE nstatus=\'pending\' LIMIT 1"
        cursor1.execute(qstr)
        #just process one pending job at a time
        for row in cursor1:    
            print('WF processing...',row)
            jobid=row[0]
            nodeid=row[1]
            wfid=row[2]
            nstatus = row[3] 
            data = row[4]
            #img_path=row[4]
            #CarCount = row[5] 
            local_data = eval(data)
            CarCount = local_data['count_cars']
            target_nid = process_message(nodeid,CarCount)

            q1 = 'DELETE FROM wf WHERE jobid=?'
            cursor1.execute(q1,(jobid,))

            q2 = ('INSERT INTO node (jobid,nodeid,wfid,nstatus,data) VALUES (?,?,?,?,?);')
            values = [jobid,target_nid,wfid,nstatus,data]
            cursor2.execute(q2,values)
            break
        # end for loop
        cursor1.commit()
        cursor2.commit()
        conn1.close()
        conn2.close()
    return 'Processing Done'
# end while






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
