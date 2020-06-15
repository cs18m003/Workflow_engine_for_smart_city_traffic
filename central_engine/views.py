"""
The codes are copyrighted to Dr. Kalidas Yeturu of IIT Tirupati. 2019/Nov/28. Please contact him at ykalidas@iittp.ac.in for permission to use these codes.
The codes are not to be distributed or used without prior permission.
The author is not liable for any damage incurred by the user of these codes.
"""
import pyodbc
from datetime import datetime
from central_engine import app
from flask import Flask, redirect, url_for, request, render_template
import pandas as pd
import pyodbc
import json
import requests
import ast
from central_engine.workflow import WFE

#these are the list of message holders
#kali_msg_list = []
condn_file = '/home/little/Documents/Workflow_new/central_engine/wf_conditions.txt'
condhand = WFE.ConditionHandler(condn_file)

wflog = WFE.WFLog()
nodelog = WFE.NodeLog()

wflog.setnodelog(nodelog)
wflog.sethandler(condhand)
nodelog.setwflog(wflog)

@app.route('/wfe/wf/strsubmit', methods=['GET'])
def wf_strsubmit() : 
    mystr = request.args.get('datastr')
    print ('received data is',mystr)
    # mydata = json.loads(mystr) # does not work
    mydata = eval(mystr)
    print ('mydata',type(mydata),mydata)
    #mydata['status'] = 'pending'
    #get a handle for the job id, this will be deleted later on
    jobid = mydata['jobid']
    nodeid = mydata['nodeid']
    wfid = mydata['wfid']
    nstatus = mydata['nstatus']
    data = mydata['data']
    print ('mydata',mydata)
    print('Job id is:{0}'.format(jobid))
    print(nodeid)
    try :
        conn1 = pyodbc.connect("Driver={MySQL ODBC 8.0 Unicode Driver};"
                  "server=localhost;"
                  "database=DbTest;"
                  "user=workflow;"
                  "password=password;"
                  "Trusted_Connection=yes;")
        cursor1 = conn1.cursor() 
        q1 = 'DELETE FROM node WHERE jobid=?'
        print(q1)
        cursor1.execute(q1,(jobid,))
        conn1.commit()
        conn1.close()

        conn2 = pyodbc.connect("Driver={MySQL ODBC 8.0 Unicode Driver};"
                  "server=localhost;"
                  "database=DbTest;"
                  "user=workflow;"
                  "password=password;"
                  "Trusted_Connection=yes;")
        cursor2 = conn2.cursor() 
        q2 = ('INSERT INTO wf (jobid,nodeid,wfid,nstatus,data) values (?,?,?,?,?);')
        print(q2)
        values = [jobid,nodeid,wfid,nstatus,str(data)]
        cursor2.execute(q2,values)
        conn2.commit()
        conn2.close()
    except :
        pass
    #end try-except
    return 'processed GET request via String'

@app.route('/wfe/wf/submit',methods = ['POST', 'GET'])
def wf_submit() :
    global wflog
    if request.method == 'POST':
        values = request.json
        mydata = {}
        mydata['jobid'] = values['jobid']
        mydata['nodeid'] = values['nodeid']
        mydata['wfid'] = values['wfid']
        mydata['nstatus'] = values['nstatus']
        mydata['data'] = values['data']
        #mydata['img_path'] = values['img_path']
        #mydata['count_cars'] = values['count_cars']
        #print(mydata)
        wflog.submit(mydata)
        return 'success: POST wf submit'
    else:
        mydata = {}
        mydata['wfid'] = request.args.get('wfid')
        mydata['status'] = 'pending'
        mydata['node'] = request.args.get('node')
        mydata['data'] = request.args.get('data')
        wflog.submit(mydata)
        return 'success: GET wf submit'

@app.route('/wfe/wf/process',methods=['GET'])
def wf_process() :
    global wflog
    wflog.process()
    return 'success: GET wf process'

@app.route('/wfe/wf/condition',methods=['GET'])
def wf_conditions() :
    condhand.refresh()
    return 'success: GET conditions loadeded'

@app.route('/wfe/node/submit',methods = ['POST', 'GET'])
def node_submit() :
    global nodelog 
    if request.method == 'POST':
        values = request.json
        mydata = {}
        mydata['mydata']={}
        mydata['jobid'] = values['jobid']
        mydata['nodeid'] = values['nodeid']
        mydata['wfid'] = values['wfid']
        mydata['nstatus'] = 'processed'
        mydata['data'] = values['data']
        #mydata['img_path'] = values['img_path']
        #mydata['count_cars'] = values['count_cars']
        nodelog.submit(mydata)   
        return 'success: POST node submit'
    else:
        mydata = {}
        mydata['wfid'] = request.args.get('wfid')
        mydata['status'] = 'pending'
        mydata['node'] = request.args.get('node')
        mydata['data'] = request.args.get('data')
        nodelog.submit(mydata)
        return 'success: GET node submit'

@app.route('/wfe/node/process/<jobid>',methods=['POST', 'GET'])
def node_process(jobid) :
    global nodelog
    nodelog.process(jobid)
    return 'success: GET node process'

@app.route('/wfe/display/<mytype>')
def display(mytype) :
    print ('display is hit',mytype)
    mylog = wflog
    if mytype=='node' :
        mylog = nodelog
    return render_template('wf_render.html',mydf=mylog.debug_getdf())


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
@app.route('/dashboard')
def dashboard():
    """Kali Dashboard is shown here"""
    return render_template(
        'dashboard.html',
        title='Dashboard',
        year=datetime.now().year,
        message='Dashboard page.'
    )

@app.route('/getjobs', methods=['GET'])
def getjobs() :
    nid = request.args.get('nodeid')
    joblist = []
    try :
        conn = pyodbc.connect("Driver={MySQL ODBC 8.0 Unicode Driver};"
                  "server=localhost;"
                  "database=DbTest;"
                  "user=workflow;"
                  "password=password;"
                  "Trusted_Connection=yes;")
        cursor = conn.cursor()
        #qstr = 'select jobid from kali_node where nodeid=\''+nid+'\' and nstatus=\'pending\' '
        qstr = 'select jobid from node where nodeid=\''+nid+'\' and nstatus=\'pending\' '
        print ('query is',qstr)
        cursor.execute(qstr)
        print ('after execution')
        #begin for loop
        for row in cursor:
            print (row)
            joblist.append(row[0])
        print ('joblist',joblist)
    except :
        pass
    #end try-except
    # return ','.join([str(x) for x in joblist]) #this works, but we show in a better way
    return render_template('node_jobs.html',joblist=joblist)

@app.route('/testit',methods=['GET'])
def testit() :
    joblist = ['a','b']
    return render_template('node_jobs.html',joblist=joblist)
    
@app.route('/renderjob',methods=['GET'])
def renderjob() :
    jid = request.args.get('jobid')
    retdict = {}
    #to actually get data from database table and load the template
    try :
        conn = pyodbc.connect("Driver={MySQL ODBC 8.0 Unicode Driver};"
                  "server=localhost;"
                  "database=DbTest;"
                  "user=workflow;"
                  "password=password;"
                  "Trusted_Connection=yes;")
        cursor = conn.cursor() 
        #cursor.execute('select * from kali_node where jobid=\''+jid+'\'')
        cursor.execute('select * from node where jobid=\''+jid+'\'')
        #begin for loop
        for row in cursor:
            # print(row)
            # business logic here
            retdict['jobid'] = row[0]
            retdict['nodeid'] = row[1]
            retdict['wfid'] = row[2]
            retdict['nstatus'] = row[3]
            #dict1=eval(row[4])
            retdict['data']=row[4]
            #retdict['img_path'] = row[4]
            #retdict['CarCount'] = row[5]
            break
        #end for loop
        cursor.close()
        conn.commit()
        conn.close()
    except :
        pass
    #end try-except
    return str(retdict)

@app.route('/renderimage',methods=['GET'])
def renderimage() :
    jid = request.args.get('jobid')
    retdict = {}
    #to actually get data from database table and load the template
    try :
        conn = pyodbc.connect("Driver={MySQL ODBC 8.0 Unicode Driver};"
                  "server=localhost;"
                  "database=DbTest;"
                  "user=workflow;"
                  "password=password;"
                  "Trusted_Connection=yes;")
        cursor = conn.cursor() 
        #cursor.execute('select * from kali_node where jobid=\''+jid+'\'')
        cursor.execute('select * from node where jobid=\''+jid+'\'')
        #begin for loop
        for row in cursor:
            # print(row)
            # business logic here
            data = eval(row[4])
            retdict['image'] = data['img_path']
            retdict['CarCount'] = data['count_cars']
            break
        #end for loop
        cursor.close()
        conn.commit()
        conn.close()
    except :
        pass
    #end try-except
    #return str(retdict)
    return render_template('image.html',retdict=retdict)



