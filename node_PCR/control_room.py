import pyodbc
import requests
from datetime import datetime
from flask import render_template
from node_PCR import app

@app.route('/process_PCR')
def process_PCR():
    conn = pyodbc.connect("Driver={MySQL ODBC 8.0 Unicode Driver};"
                  "server=localhost;"
                  "database=DbTest;"
                  "user=workflow;"
                  "password=password;"
                  "Trusted_Connection=yes;")
    cursor = conn.cursor()
    qstr = "SELECT * FROM node WHERE nodeid=\'node_PCR\' AND nstatus=\'pending\' "
    #print ('query is',qstr)
    cursor.execute(qstr)
    print ('Stand by for message to PCR')
    #begin for loop
    for row in cursor:
        jobid = row[0]
        local_data = eval(row[4])
        CarCount = local_data['count_cars'] 
        print ('joblist: ',jobid, 'CarCount: ',CarCount, ' has been sent to PCR van to report at the spot')

    url = "https://www.fast2sms.com/dev/bulk"
    payload = "sender_id=FSTSMS&message=there is heavy traffic near your junction. the car count is "+str(CarCount)+"&language=english&route=p&numbers=8597226279"
    headers = {
    'authorization': "JDmw9PWrgSzXFQn7RyhkNjYMp3qBGL5eUHsViKaxo4bZT08OC1ZYCIBUdyGju6RpMFfrctSDVP0zismX",
    'Content-Type': "application/x-www-form-urlencoded",
    'Cache-Control': "no-cache",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)
    return 'PCR has sent the message' 

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
