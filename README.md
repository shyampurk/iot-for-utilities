#Tracking Electricity with IBM Bluemix and PubNub

#Introduction 

This is a project that demonstrates how can we track the electricity consumption of a household using IoT. This is based upon a miniature DC model of electric network within a house which is monitored by a few current sensors and Arduino YUN.

#Project Overview
The project consits of a model electricity distribution network for a home, a server application and a web dashboard.

The model electric distribution network consists of

1.  A househuld electricity distribution network with two loads, a light and a fan, each having a switch to control them.
2.  A 12 volt, lead acid AT12 battery that acts as a grid to supply electricity to the household.
3.  A solar panel (18V, 10W) used as a renewable source of energy
4.  Three current sensors (ACS712) to measure current and calculate kWH of consumption and generation across the house.
5.  Arduino YUN as controller for the current sensors and sending the calculations to cloud.

A server application hosted on IBM Bluemix and keeps track of the energy consumption and generation at various points of the electric distribution.   

A web dashboard presents a real time view of the energy usage in the house, based on the usage of loads.

#Setup

## General Prerequisites

- This application relies on  PubNub data stream network for the underlying messaging between the hardware, the server and dashboard. Ensure that the same set of PubNub keys are used across all the components while configuring and building the application software. 

- Ensure that you have signed up for IBM Bluemix and PubNub subscription.

## Hardware setup

### Building the model electricity distribution circuit with solar cell and battery.

The schematic diagram for the entire circuit setup is as follows.

<img src="/screenshots/schematic.png" align="center" width="600" >

### Arduino YUN Controller application

The Arduino YUN acts as the controller for sensing the current measurements.

The source code for the controller software can be built using the Makefile. There are two phases involved in the build.

#### Master Controller build

##### Build Environment Setup

The master controller is the OpenWRT application running on YUN. Before initiating the build, we need to setup the build environment on the YUN since we will be using the Adruino YUN environment itself for building the software

Step 1 : Install yun-gcc to Arduino YUN 

	(i)	Before installing yun-gcc, install the 	following 

			opkg update
			opkg install binutils
			opkg install make
			opkg install tar

	(ii)	Now we are ready to install the yun-gcc,

			opkg -t /root install yun-gcc

This package will take about 20 minutes or more to install so be patient, once it finishes you will be ready to compile simple c or c++ programs.It is prefered to download and install this package separately so that we can see what is going on:
				
			cd /mnt/sda1
			wget http://downloads.arduino.cc/openwrtyun/1/packages/yun-gcc_4.6.2-2_ar71xx.ipk
			opkg install yun-gcc_4.6.2-2_ar71xx.ipk

Step 2 : Installing the glibc 

	(i)	Download the Package glibc-source_2.19-18+deb8u1_all.deb in your laptop from the following link 

			https://packages.debian.org/jessie/all/glibc-source/download

	(ii)	Once the package is downloaded SCP the file to the YUN using the following command running on the 	
			new terminal(modify the filename and IP address)

			scp -r Downloads/(filename).deb root@192.168.XX.XX:/root/

	(iii)	Once done install the glibc,

			opkg -f /etc/opkg.conf -d ram update 
			opkg -f /etc/opkg.conf -d ram install <package-name>

Now Arduino-YUN is ready to compile and run the C Programs.

Step 3: Edit the /etc/inittab file for UART Communication

			nano /etc/inittab
				
Comment out the ttyATH0 line by adding # as prefix and save the file.				

##### Master Build

Steps to be followed to build the Master Controller software of IoT for Utilities application on Arduino YUN

Step 1: Clone this repository bluemix-parking-meter from the github in your laptop/PC

    			git clone https://github.com/shyampurk/iot-for-utilities/

Step 2: Change the directory to the iot-for-utilities 

    			cd iot-for-utilities

Step 3: Clone the c-core library from the pubnub

    			git clone https://github.com/pubnub/c-core.git

Step 4: Copy iot-for-utilities folder using SCP to the YUN

			scp -r iot-for-utilities root@192.168.XX.XX:/root/

Step 5: Open up the terminal and follow the commands, make sure you know the IP address of the Arduino-YUN
			
			ssh root@yourname/local or ssh root@192.168.XX.XX	

Step 6: Change the directory to the bluemix-parking-meter 

    			cd iot-for-utilities 

Step 7:	Modify the Pubnub Publish and Subscribe Keys in the yun_pubnub/main.c

Step 8: To Build using the Makefile, just run

    			make

Step 9: You should see the executable file named ./solarMeter. This is the master controller program. To execute this program, run the file as follows.
			
			./solarMeter /dev/ttyATH0
			
			(where /dev/ttyATH0 is path of the UART device file)

#### Sensor Controller Build

Sensor controller build is for programming onboard the ATMega32 MCU which intefaces with the current sensors.

Before preceeding, we need to install Arduino IDE 

Installing the Arduino IDE

	- Download and Install Latest Version of Arduino IDE from 

                	[https://www.arduino.cc/en/Main/Software]

	- Start Arduino IDE and Plug the Development Board

Step 1: Open the file device/current_sense_new/current_sense_new.ino from this repo in Arduino IDE

Step 2: Select the Board from Tools - > Board - > Arduino YUN

Step 3: Select the USB Port from Tools - > Port - > yourname @ ipaddress [Arduino-YUN]

Step 4: Upload the Code




## Server Setup

The server has a DashDB component which provides a data store for capturing realtime energy usage data.

### Deploying DashDB Service

Step 1: Login to Bluemix with your credentials.

Step 2: In your Bluemix dashboard, goto Catalog and select the Data and Analytics Section
			
			You can see that the dashDB service will be listed under this section or you can search for dashDB 

Step 3: Click on dashDB service icon and create a dashDB service instance for your space by filling following details,
		
			1) Space - Your space name where you want to add this service ( This might have been preselected if you have an existing space)
    			2) App   - You can select "leave unbound"
			3) Service name - Enter a name for the service of your choice
			4) Credential name - Enter a name for the Credential of your choice
			5) Selected Plan - Choose 'Entry'.
			6) Click CREATE to create the dashdb service instance.

Step 4: After creation of the service, go back to dashboard.Now you can see the dashDB service added to your space. Click the service and click the launch button and you can see your newly created dashDB service home page.

Step 5: In the dashDB service home page, under the Side Menu, under the Connect -> Connection information, 
		
	You can see your dashDB Host name,Database name,user id and password.

        Make a note of Host Name, Port Number , Database Name, User ID and Password.

Step 6: In the Side Main Menu, click on "Run SQL"  and you will be presented the Run SQL screen. Click on the 'Open' button and choose the SQL [schema file](powerGrid_server/dashDB.sql)

		- The SQL command (CREATE_TABLE) will be displayed in the text area.
		- Click on the 'Validate' button to ensure that SQL syntax is valid
		- Click on the 'Run' button to execute the SQL statements.

Step 7: If the Run command executed successfully , you will be able to see the new tables created under your dashDB instance
		
		- Click on "Tables" sub menu
		- Select the table from "Table Name" dropdown to access the table schema and data
		- You can find the tables named "IOT_ENERGYGRID_TABLE" listed under the dropdown
		





### Hosting the Application Server on Bluemix



Step 1 - Update the parameters in the server [config file](powerGrid_server/config.ini) 

	pub_key = PubNub Publish Key
	sub_key = PubNub Subscribe Key
	databaseschema = User ID of the DashDB instance , in caps
	databasename = Database name
	hostname  = Database Host Name
	tablename = Table name is set to KITCHENTRACKERAPP
	userid = User ID of the DashDB instance
	password = Password of dashDB instance
	portnumber = Port Number
	expiry = 0 ( Leave it to default value of zero)
	

Step 2 - Open the [manifest file](powerGrid_server/manifest.yml) and update the follwing entries

	Line 12 - Change 'IoTEnergyGrid_DashDB' to the actual dashDB service name you have given while creating the dashDB service instance ( Step 3 in 'Deploying DashDB Service').


Step 3 - Login to Bluemix console via cf tool and select the space.

Step 4 - Change directory to the server application root directory (powerGrid_server) under the cloned github repository.

Step 5 - Run the following command to push the application code to bluemix

		'cf push' 

Once successfully pushed, the server application will be automatically started. You can check its state in your bluemix dashboard and see that it is set to 'Running'

## Web Dashboard
Once the application server is up on Bluemix, you can launch the web dashboard. 

<img src="/screenshots/dashboard_snap.jpg" align="center" width="600" >

# Application working
Fire up the circuit and you can see the energy stats getting captured in server DashDB and also displayed on the dashboard.
The behaviour of the application will primarily depend on the power output of solar panel. It is advisable to test this with the solar panels exposed under sunny conditions.

<img src="/screenshots/dashboard_demo_final.gif" align="center" width="900" >
