# IMPORTING THE REQUIRED MODULES
import ibm_db
import os
import sys
from ibm_db import connect
from ibm_db import active
from pubnub import Pubnub
import time
import logging
import datetime

# Database connection information
databaseConnectionInfo = {"Database name":"BLUDB","User ID":"dash6278","Password":"xdS5nnFhY8kq","Host name":"dashdb-entry-yp-dal09-10.services.dal.bluemix.net","Port number":"50000"}
DatabaseSchema = 'DASH6278'

# PUBNUB KEYS
pub_key ='pub-c-06039a79-c423-4a3f-a838-30d86ee08a5e'
sub_key ='sub-c-8bafb53a-682a-11e6-933d-02ee2ddab7fe'

LOG_FILENAME = 'IoTEnergyGrid_Logs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


'''****************************************************************************************
Function Name 	:	connectioncheck_handler() (dB operation)
Description		:	Function to check the connection to the DataBase is True/False
Parameters 		:	- 
****************************************************************************************'''

def connectioncheck_handler():
	global connection,url
	if (active(connection) == False):
		connection = ibm_db.pconnect(url ,'' ,'')
	return None	




'''****************************************************************************************
Function Name 	:	publish_handler  (pubnub operation)
Description		:	Function used to publish the data to the client
Parameters 		:	channel          - Name of the Table in DataBase from where Data is being Extracted					  
****************************************************************************************'''

def publish_handler(channel,result):
	pbtry = 0
	while (pbtry<3):
		try:
			pbreturn = pubnub.publish(channel = channel ,message = result,error=error)
			
			if (pbreturn[0] == 1):
				return None
			elif(pbreturn[0] == 0):
				logging.error("The publish return error  %s for the Task %s for the client %s"%(pbreturn[1],channel,details['DISPLAY_NAME']))
				pbtry+=1
			else:
				pass
		except Exception as error_pdhandler:
			logging.error("The publish function Exception %s,%s for the Task %s for the client %s"%(error_pdhandler,type(error_pdhandler),channel,details['DISPLAY_NAME']))
			pbtry+=1


'''****************************************************************************************
Function Name 	:	dBop_Insert  (dashdB operation)
Description		:	Function used to insert the Data to the Table in DataBase 
Parameters 		:	message(Dictionary that contains the Current and Energy values)
****************************************************************************************'''
def dBop_Insert(message):
	global connection
	connectioncheck_handler()	
	try:	
		upload_query = "INSERT INTO "+DatabaseSchema+".IOT_ENERGYGRID_TABLE VALUES (DEFAULT,\'"+str(message["Current1"])+"\',\'"+str(message["Current2"])+"\',\'"+str(message["Current3"])+"\',\'"+str(message["Energy1"])+"\',\'"+str(message["Energy2"])+"\',\'"+str(message["Energy3"])+"\',\'"+str(message["TotalEnergy"])+"\',\'"+str(message["Time"])+"\')"
		stmt = ibm_db.exec_immediate(connection, upload_query)
		ibm_db.free_stmt(stmt)
	except Exception as e:
		logging.error("The error in dBop_Insert is %s,%s"%(e,type(e)))


# Data format from the Device
# Dict = {"001":[load_1_status,load_2_status,current1,energy1,current2,energy2,current3,energy3]}

'''****************************************************************************************
Function Name 	:	callback
Description		:	Callback function listens to the channel for the messages
Parameters 		:   message  - message from the client
					channel  - channel used for communication between client and the server
****************************************************************************************'''

def callback(message,channels):
	logging.info("Message from the Device",message)
	channel = "IoTEnergyGrid-App" # App channel name
	
	if int(message["001"][0]) == 1 and int(message["001"][1] == 1):
		grid = 1
	else:
		grid = 0

	pubDict = {"load_1_status":message["001"][0],"load_2_status":message["001"][1],"Current1":message["001"][2],"Current2":message["001"][4],"Current3":message["001"][6],"Grid":grid}
	publish_handler(channel,pubDict)		
	dbmessage = pubDict
	time = datetime.datetime.utcnow().replace(microsecond=0)
	TotalEnergy = message["001"][3] + message["001"][5] + message["001"][7]
	dbmessage.update({"Energy1":message["001"][3],"Energy2":message["001"][5],"Energy3":message["001"][7],"TotalEnergy":TotalEnergy,"Time":time})
	dBop_Insert(dbmessage)

'''****************************************************************************************
Function Name 	:	error
Description		:	If error in the channel, prints the error
Parameters 		:	message - error message
****************************************************************************************'''
def error(message):
    logging.error("ERROR on Pubnub: " + str(message))

'''****************************************************************************************
Function Name 	:	connect
Description		:	Responds if server connects with pubnub
Parameters 		:	message - connect message
****************************************************************************************'''	
def connect(message):
	logging.info("CONNECTED")

'''****************************************************************************************
Function Name 	:	reconnect
Description		:	Responds if server reconnects with pubnub
Parameters 		:	message - reconnect message
****************************************************************************************'''	
def reconnect(message):
    logging.info("RECONNECTED")

'''****************************************************************************************
Function Name 	:	disconnect
Description		:	Responds if server disconnects from pubnub
Parameters 		:	message - disconnect message
****************************************************************************************'''
def disconnect(message):
     logging.info("DISCONNECTED")



'''****************************************************************************************
Function Name 	:  channel_subscriptions
Description		:  Function for subscribing to the channel 
Parameters 		:  -
****************************************************************************************'''
def channel_subscriptions():
	global pubnub
	try:
		pubnub.subscribe(channels='IoTEnergyGrid-Device', callback=callback,error=error,
		connect=connect, reconnect=reconnect, disconnect=disconnect)
	except Exception as channelsubserror:
		logging.error("The error in channel_subscriptions is %s,%s"%(channelsubserror,type(channelsubserror)))


'''****************************************************************************************
Function Name 	:	pub_Init
Description		:	Function to initiate the pubnub
Parameters 		:   - 
****************************************************************************************'''
	
def pub_Init():
	global pubnub
	
	try:
		pubnub = Pubnub(publish_key=pub_key,subscribe_key=sub_key) 
		return True
	except Exception as pubException:
		logging.error("The error in pub_Init is %s,%s"%(pubException,type(pubException)))
		return False


'''****************************************************************************************
Function Name 	:	dashdB_Init
Description		:	Initalize the Database and establishing the connection between the 
					database and the kitchen-tracker
Parameters 		:	None
****************************************************************************************'''

def dashdB_Init():
	global connection,url
	dbtry = 0
	while(dbtry <3):
		try:
			if 'VCAP_SERVICES' in os.environ:
			    hasVcap = True
			    import json
			    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
			    if 'dashDB' in vcap_services:
			        hasdashDB = True
			        service = vcap_services['dashDB'][0]
			        credentials = service["credentials"]
			        url = 'DATABASE=%s;uid=%s;pwd=%s;hostname=%s;port=%s;' % ( credentials["db"],credentials["username"],credentials["password"],credentials["host"],credentials["port"])
			    else:
			        hasdashDB = False
			  
			else:
			    hasVcap = False
			    url = 'DATABASE=%s;uid=%s;pwd=%s;hostname=%s;port=%s;' % (databaseConnectionInfo["Database name"],databaseConnectionInfo["User ID"],databaseConnectionInfo["Password"],databaseConnectionInfo["Host name"],databaseConnectionInfo["Port number"])
   
			connection = ibm_db.connect(url, '', '')
			if (active(connection)):
				return connection
		except Exception as dberror:
			logging.error("dberror Exception %s"%dberror)
			dbtry+=1
	return False


'''****************************************************************************************
Function Name 	:	Init()
Description		:	Function which starts all the operations
Parameters 		:   -
****************************************************************************************'''
def Init():
	dBreturn = dashdB_Init()
	pbreturn = pub_Init()
	if (dBreturn == False or pbreturn == False):
		logging.error("Program Terminated")
		sys.exit()
	else:
		channel_subscriptions()



if __name__ == '__main__':
	Init()     