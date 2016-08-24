
pubnub = PUBNUB({                          
    publish_key   : 'pub-c-06039a79-c423-4a3f-a838-30d86ee08a5e',
    subscribe_key : 'sub-c-8bafb53a-682a-11e6-933d-02ee2ddab7fe'
});

var sunsolPan,solPanhome,homeS1,homeS2,gridS3,s2Grid,s2Bulb,s2Fan,s3Bulb,s3Fan;
var bulb;
var fan;
var grid;
var bulbOn = "#FFDB55";
var bulbOff = "#000000";
var red = "#b00b1e";
var green = "#32cd32";
var sm,sbulb,sfan,sgrid,sen1,sen2,sen3;


/****************************************************************************************************
	Function 	: HTML SVG Connect
	Description : draws connection line between two img/svg  
*****************************************************************************************************/		
		function lineColour(sbulb,sfan,sgrid){

			console.log("The line colour function","Load1:",sbulb,"Load2",sfan,"Grid",sgrid)
			bulb = sbulb;
			fan = sfan;
			grid = sgrid;
			$svg = $("#svgPaths");
			if(grid == 1){
	    		$("#1", $svg).attr('style', "stroke:"+green);
	    		$("#2", $svg).attr('style', "stroke:"+green);
	    		$("#3", $svg).attr('style', "stroke:"+green);
	    		$("#4", $svg).attr('style', "stroke:"+red);
	    		$("#5", $svg).attr('style', "stroke:"+green);
	    		$("#6", $svg).attr('style', "stroke:"+green);
	    		$("#7", $svg).attr('style', "stroke:"+red);
	    		$("#8", $svg).attr('style', "stroke:"+green);
	    		$("#9", $svg).attr('style', "stroke:"+green);
		    }
		    else{
	    		$("#1", $svg).attr('style', "stroke:"+green);
	    		$("#2", $svg).attr('style', "stroke:"+green);
	    		$("#3", $svg).attr('style', "stroke:"+green);
	    		$("#4", $svg).attr('style', "stroke:"+green);
	    		$("#5", $svg).attr('style', "stroke:"+red);
	    		$("#6", $svg).attr('style', "stroke:"+green);
	    		$("#7", $svg).attr('style', "stroke:"+green);
	    		$("#8", $svg).attr('style', "stroke:"+red);
	    		$("#9", $svg).attr('style', "stroke:"+green);
	    	}
			if(bulb == 0 && fan == 0){
	    		$("#10", $svg).attr('style', "stroke:"+red);
	    		$("#11", $svg).attr('style', "stroke:"+red);
		    }
	    	else if(bulb == 0 && fan == 1){
	    		$("#10", $svg).attr('style', "stroke:"+red);
	    		$("#11", $svg).attr('style', "stroke:"+green);
	    	}
		    else if(bulb == 1 && fan == 0){
	    		$("#10", $svg).attr('style', "stroke:"+green);
	    		$("#11", $svg).attr('style', "stroke:"+red);
	    	}
		    	
		    else if(bulb == 1 && fan == 1){
	    		$("#10", $svg).attr('style', "stroke:"+green);
	    		$("#11", $svg).attr('style', "stroke:"+green);
	    	}
		    	

		    if(bulb == 1){
		    	var bulbElement = document.getElementById("onOff")
		    	bulbElement.setAttribute("fill", bulbOn);
		    }
		    else{
		    	var bulbElement = document.getElementById("onOff")
		    	bulbElement.setAttribute("fill", bulbOff);
		    }
		    if(fan == 1){
		    	var fanElement = document.getElementById("fan");
				fanElement.src = "image/Fan-02.gif"
		    }
		    else{
		    	var fanElement = document.getElementById("fan");
				fanElement.src = "image/Fan-02.jpg"
		    }
		}
/****************************************************************************************************
	Function 	: D3 based ammeter gauge
	Description	: creates gauge displaying current readings (Amps) from the current sensor
******************************************************************************************************/
		var gauges = [];
		
		function createGauge(name, label, min, max)
		{
			var config = 
			{
				size: 140,
				label: label,
				min: undefined != min ? min : 0,
				max: undefined != max ? max : 20,
				minorTicks: 5
			}
			
			var range = config.max - config.min;
			config.yellowZones = [{ from: config.min + range*0.75, to: config.min + range*0.9 }];
			config.redZones = [{ from: config.min + range*0.9, to: config.max }];
			
			

			gauges[name] = new Gauge(name + "Gauge", config);
			gauges[name].render();
		}
		
		function createGauges()
		{
			createGauge("sensor1", "Amps",0,2);
			createGauge("sensor2", "Amps",0,2);
			createGauge("sensor3", "Amps",0,2);
		}
		
		function updateGauges(ssensor1,ssensor2,ssensor3)
		{
			for (var key in gauges)
			{
				if(key == "sensor1"){
					var value1 = ssensor1;
					console.log("The Current1:",value1)
					gauges[key].redraw(value1);
				}
				else if(key == "sensor2"){
					var value2 = ssensor2;
					console.log("The Current2:",value2)
					gauges[key].redraw(value2);
				}
				else if(key == "sensor3"){
					var value3 = ssensor3;
					console.log("The Current3:",value3)
					gauges[key].redraw(value3);
				}
			}
		}

		function sleep(milliseconds) {
		  	var start = new Date().getTime();
		  	for (var i = 0; i < 1e7; i++) {
		    	if ((new Date().getTime() - start) > milliseconds){
		    		break;
		    	}
		  	}
		}
/********************************************************************************************************************
	Function 	: PUBNUB pub/sub
	Description	: subscribes to the server displaying load on/off state and current usage
*********************************************************************************************************************/
		$(document ).ready(function() {

			createGauges();
	        pubnub.subscribe({
	            channel: "IoTEnergyGrid-App",
				message: function(sm){
					sbulb = sm.load_1_status //bulb
					sfan = sm.load_2_status  //fan
					sgrid = sm.Grid
					sen1 = sm.Current_ToGrid
					sen2 = sm.Current_SolarSupply
					sen3 = sm.Current_GridSupply
					// console.log(sm)
					console.log("Load1:",sm.load_1_status,"Load2:",sm.load_2_status,"Grid:",sm.Grid)
					console.log("Current_ToGrid:",sm.Current_ToGrid,"Current_SolarSupply:",sm.Current_SolarSupply,"Current_GridSupply:",sm.Current_GridSupply)

					if(sm == "undefined"){
						console.log("undefined section")
						lineColour(0,0,0);
						updateGauges(0,0,0);	
					}
					else if(sm == ""){
						console.log("empty section")
						lineColour(0,0,0);
						updateGauges(0,0,0);	
					}
					else{
						console.log("else section")
						lineColour(sbulb,sfan,sgrid);
						updateGauges(sen1,sen2,sen3);
					}
					
				},
				error: function (error) {
                  	console.log(JSON.stringify(error));
				}
			})	
		});
/**********************************************************************************************************************
***********************************************************************************************************************/
