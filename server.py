from flask import Flask
import sqlite3
import datetime
import io
import base64
import matplotlib.pyplot as plt
import math
import smtplib,os,time

#Send Mail
def sendAlert(msg,url):
	message = 'Subject: {}\n\n{}'.format('Alert: Leakage detected', msg)
	server=smtplib.SMTP("smtp.gmail.com:587")
	server.ehlo()
	server.starttls()
	server.login("testiotsap@gmail.com","dynamo2018")
	server.sendmail("ankitvi.2818.av@gmail.com","priteshsatpute1998@gmail.com",message)
	server.quit()

app = Flask(__name__)

#Global variables
threshold = 7
count = 0
leakage = 0

#Create database if not exists
conn = sqlite3.connect('database.db')
try:
	conn.execute('CREATE TABLE sensors (sid TEXT, svalue INTEGER, stime TEXT)')
	conn.close()
except:
	conn.close()

#Get data from sensors
@app.route('/<sensor1>/<sensor2>')
def putData(sensor1,sensor2):
	global count
	global leakage
	s1id = '1'
	s2id = '2'			
	sensor1 = float(sensor1)
	sensor2 = float(sensor2)
	print(count)

	#Insert values into database
	timestamp = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())#'0'
	with sqlite3.connect("database.db") as con:
		cur = con.cursor()
		cur.execute('INSERT INTO sensors values(?,?,?)',(s1id,str(sensor1),timestamp))#str(datetime.datetime.now().time())))
		con.commit()

	with sqlite3.connect("database.db") as con:
		cur = con.cursor()
		cur.execute('INSERT INTO sensors values(?,?,?)',(s2id,str(sensor2),timestamp))#str(datetime.datetime.now().time())))
		con.commit()							

	#Check for leakage	
	if (abs(sensor2-sensor1))>threshold:
		count = count + 1
		if(count>=5):
			leakage = abs(sensor2-sensor1)
			msg = '[SAP] Leakage of '+str(abs(sensor2-sensor1))+' ml between Sensor '+s1id+' and Sensor '+s2id
			sendAlert(msg,"192.0.0.168:8080")
			print(msg)
			return msg
		else:
			return '[SAP] No Leakage detected'
				
	else:
		count = 0
		return '[SAP] No Leakage detected'


#Returns the current status of the system	
@app.route('/isLeakage')
def isLeakage():
	global leakage
	if(count>=5):
			msg = '<h1>[SAP] Leakage of '+str(leakage)+' ml between Sensor 1 and Sensor 2</h1>'
			sendAlert(msg,"192.0.0.168:8080")
			print(msg)
			return msg
	else:
			return '<h1>[SAP] No Leakage detected<h1>'


#Returns all the values of sensors with timestamp
@app.route('/visualize')
def visualize():
	graph = io.BytesIO()
	conn = sqlite3.connect('database.db')
	cur = conn.cursor()
	cur.execute('SELECT *FROM sensors')
	rows = cur.fetchall()
	return str(rows)


#Run server on local IP and port 8080
if __name__ == '__main__':
   app.run('0.0.0.0',8080,True)