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

import ConfigParser

LOG_FILENAME = 'IoTEnergyGrid_Logs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')



#Importing the Config File and Parsing the file using the ConfigParser
config_file = "./config.ini"
Config = ConfigParser.ConfigParser()
Config.read(config_file)


'''****************************************************************************************
Function Name 	:	ConfigSectionMap
Description		:	Parsing the Config File and Extracting the data and returning it
Parameters 		:	section - section to be parserd
****************************************************************************************'''
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            logging.debug("exception on %s!" % option)
            dict1[option] = None
    return dict1

# Initialize the Pubnub Keys 
PUB_KEY = ConfigSectionMap("pubnub_init")['pub_key']
SUB_KEY = ConfigSectionMap("pubnub_init")['sub_key']

#Database Related Variables and Lists 
DB_SCHEMA = ConfigSectionMap("database")['databaseschema'] 
DB_HOST = ConfigSectionMap("database")['hostname']
DB_NAME = ConfigSectionMap("database")['databasename']
DATABASE_TABLE_NAME = ConfigSectionMap("database")['tablename']
DB_USER_NAME = ConfigSectionMap("database")['userid']
DB_PASSWORD = ConfigSectionMap("database")['password']
DB_PORT = ConfigSectionMap("database")['portnumber']




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
Parameters 		:	channel  - Name of the Table in DataBase from where Data is being Extracted
					result   - Dictionary that contains the values to be sent to the client								  
****************************************************************************************'''
def publish_handler(channel,result):
	pbtry = 0
	while (pbtry<3):
		try:
			pbreturn = pubnub.publish(channel = channel ,message = result,error=error)
			
			if (pbreturn[0] == 1):
				return None
			elif(pbreturn[0] == 0):
				logging.error("The publish return error  %s for the Task %s for the client %s"%(pbreturn[1],channel))
				pbtry+=1
			else:
				pass
		except Exception as error_pdhandler:
			logging.error("The publish function Exception %s,%s for the Task %s for the client %s"%(error_pdhandler,type(error_pdhandler),channel))
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
		upload_query = "INSERT INTO "+DB_SCHEMA+"."+DATABASE_TABLE_NAME+" VALUES (DEFAULT,\'"+str(message["Current_ToGrid"])+"\',\'"+str(message["Current_SolarSupply"])+"\',\'"+str(message["Current_GridSupply"])+"\',\'"+str(message["Energy_ToGrid"])+"\',\'"+str(message["Energy_SolarSupply"])+"\',\'"+str(message["Energy_GridSupply"])+"\',\'"+str(message["TotalEnergy"])+"\',\'"+str(message["Time"])+"\')"
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
	try:
		print message	
		logging.info("Message from the Device"+str(message))
		channel = "IoTEnergyGrid-App" # App channel name
		
		if int(message["001"][0]) == 1 and int(message["001"][1] == 1):
			grid = 1
		else:
			grid = 0


		pubDict = {"load_1_status":message["001"][0],"load_2_status":message["001"][1],"Current_ToGrid":message["001"][2],"Current_SolarSupply":message["001"][4],"Current_GridSupply":message["001"][6],"Grid":grid}
		publish_handler(channel,pubDict) #Calling the pubnub publish function		
		dbmessage = pubDict

		# Getting the present UTC Time
		time = datetime.datetime.utcnow().replace(microsecond=0)

		#Calculating the Total Energy 
		TotalEnergy = message["001"][3] + message["001"][5] + message["001"][7]
		
		dbmessage.update({"Energy_ToGrid":message["001"][3],"Energy_SolarSupply":message["001"][5],"Energy_GridSupply":message["001"][7],"TotalEnergy":TotalEnergy,"Time":time})
		
		dBop_Insert(dbmessage)  # Calling dashDB data upload function
	except Exception as e:
		logging.error("The error in callback %s,%s"(e,type(e)))	
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
		pubnub = Pubnub(publish_key=PUB_KEY,subscribe_key=SUB_KEY) 
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
			    url = 'DATABASE=%s;uid=%s;pwd=%s;hostname=%s;port=%s;' % (DB_NAME,DB_USER_NAME,DB_PASSWORD,DB_HOST,DB_PORT)
   
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