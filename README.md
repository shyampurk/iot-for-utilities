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

The schematic diagram for the hardware setup is as follows.

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
