#Tracking Electricity with IoT using IBM Bluemix and PubNub

#Introduction 

This is a project that demonstrates how can we track the electricity consumption of a household using IoT. This is based upon a miniature DC model of electric network within a house which is monitored by a few current sensors and Arduino YUN.

#Setup
The project setup consits of a model electricity distribution network for a home, a server application and a web dashboard.

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

Step 2: In your dashboard, goto Catalog and select the Data and Analytics Section
			
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

Step 6: In the Side Main Menu click Tables,Here you can create the table for this application.
		Click 'Add Table' to create the table for kitchen tracking application by entering the below SQL stamement in the bottom text area.
		
    CREATE TABLE "ENERGY" 
    (
      "SCALE_ID" VARCHAR(3),
      "DATES" DATE,
      "TIME" VARCHAR(10),
      "QUANTITY" FLOAT,
      "STATUS" INT 
    );



Step 7: Then click the button "Run DDL".
		You can see the newly created table by selecting your schema and table name. Your schema is same as your username as displayed in Connect > Connection Information menu.

### Deploying the Application Server

Step 1 - Clone this github repository

Step 2 - Update the parameters in the [config.ini]

	pub_key = PubNub Publish Key
	sub_key = PubNub Subscribe Key
	db_schema = User ID of the DashDB instance , in caps
	db_name = Database name
	db_host = Host Name
	table_name = Table name is set to KITCHENTRACKERAPP
	username = User ID of the DashDB instance
	pwd = Password of dashDB instance
	port = Port Number
	expiry = 0 ( Leave it to default value of zero)
	

Step 3 - Open the [manifest file] and update the follwing entries

		applicationa:
			- name : <name of the application on server>
	
		services
			- <dashdb instance name>

		where 
			<name of the application on server> - Any desired name for the application
			<dashdb instance name> - name of the dashdb service instance that you have created in the previous section.


Step 4 - Login to Bluemix console via cf tool and select the space.

Step 5 - Change directory to the server application root (kitchen_tracker) under the cloned github repository.

Step 6 - Run the following command to push the application code to bluemix

		'cf push' 

Once successfully pushed, the server application will be automatically started. You can check its state in your bluemix dashboard and see that its state is set to 'Running'



  

