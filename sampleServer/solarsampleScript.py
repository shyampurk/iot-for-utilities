from pubnub import Pubnub
import time
import random
from random import randint

pub_key ='demo'
sub_key ='demo'


'''****************************************************************************************
Function Name 	:	error
Description		:	If error in the channel, prints the error
Parameters 		:	message - error message
****************************************************************************************'''
def error(message):
    print("ERROR on Pubnub: " + str(message))

'''****************************************************************************************
Function Name 	:	connect
Description		:	Responds if server connects with pubnub
Parameters 		:	message - connect message
****************************************************************************************'''	
def connect(message):
	print("CONNECTED")

'''****************************************************************************************
Function Name 	:	reconnect
Description		:	Responds if server reconnects with pubnub
Parameters 		:	message - reconnect message
****************************************************************************************'''	
def reconnect(message):
    print ("RECONNECTED")

'''****************************************************************************************
Function Name 	:	disconnect
Description		:	Responds if server disconnects from pubnub
Parameters 		:	message - disconnect message
****************************************************************************************'''
def disconnect(message):
     print("DISCONNECTED")
def main():
	while True:
		bulb = random.randint(0,1)
		fan = random.randint(0,1)
		grid = random.randint(0,1)
		C1 = random.randint(0,3)
		C2 = random.randint(0,3)
		C3 = random.randint(0,3)
		pubDict = {"bulb":bulb,"fan":fan,"grid":grid,"sensor1":C1,"sensor2":C2,"sensor3":C3}
		pubnub.publish(channel = "aravind" ,message =pubDict,error=error)
		time.sleep(10)


def callback(message,channels):
	print message
def channel_subscriptions():
	global pubnub
	try:
		pubnub.subscribe(channels='aravind', callback=callback,error=error,
		connect=connect, reconnect=reconnect, disconnect=disconnect)
		main()
	except Exception as channelsubserror:
		print channelsubserror


def pub_Init():
	global pubnub
	
	try:
		pubnub = Pubnub(publish_key=pub_key,subscribe_key=sub_key) 
		channel_subscriptions()
		# return True
	except Exception as pubException:
		print pubException
		return False

if __name__ == '__main__':
	pub_Init()	