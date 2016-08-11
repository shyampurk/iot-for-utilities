
/*******************************************************************************************************
 *                                        SMART ENERGY UTILITIES                                         *
 *******************************************************************************************************/

//Load Control and Status Pins
#define RELAY_PIN     7
#define LOAD_PIN_1    11
#define LOAD_PIN_2    12
#define SWITCH_PIN_1  8
#define SWITCH_PIN_2  9

//Current Sensor Pins
#define CURRENT_SENSOR_1  A0
#define CURRENT_SENSOR_2  A3
#define CURRENT_SENSOR_3  A1

//Variables for the Load 1
double g_current  = 0.0;
float g_totamps   = 0.0; 
float g_avgamps   = 0.0;
float g_amphr     = 0.0;
float g_watt      = 0.0;
float g_energy    = 0.0;

//Variables for the Load 2
double g_current_1= 0.0;
float g_totamps_1 = 0.0; 
float g_avgamps_1 = 0.0;
float g_amphr_1   = 0.0;
float g_watt_1    = 0.0;
float g_energy_1  = 0.0;

//Variables for the Load 3
double g_current_2= 0.0;
float g_totamps_2 = 0.0; 
float g_avgamps_2 = 0.0;
float g_amphr_2   = 0.0;
float g_watt_2    = 0.0;
float g_energy_2  = 0.0;

//Offset for the Current Sensor
float g_offset    = 512.0;

/*******************************************************************************************************
 Function Name            : setup
 Description              : Initialize the Pins and Serial Bridge Port
 Parameters               : None
 *******************************************************************************************************/
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial1.begin(9600);

  //Initialize the Load Control & Currents Sensor pins to output
  pinMode(RELAY_PIN,OUTPUT);
  pinMode(LOAD_PIN_1,OUTPUT);
  pinMode(LOAD_PIN_2,OUTPUT);

  //Initialize the Load Sensing pins to Input
  pinMode(SWITCH_PIN_2,INPUT);
  pinMode(SWITCH_PIN_1,INPUT);
  pinMode(CURRENT_SENSOR_1,INPUT);
  pinMode(CURRENT_SENSOR_2,INPUT);
  pinMode(CURRENT_SENSOR_3,INPUT);
}

/*******************************************************************************************************
 Function Name            : sensor_input
 Description              : Obtain the current value in each sensor
 Parameters               : None
 *******************************************************************************************************/
float sensor_input(int p_pin){
  float l_analogValue = 0.0;
  float l_actualval = 0.0;
  for (int i = 0;i< 150;i++){
    l_analogValue += analogRead(p_pin);
    delay(5);  
  }
  l_analogValue = l_analogValue / 150;
  if(p_pin == 19 && l_analogValue >= 50) l_actualval = 400 - l_analogValue;
  else l_actualval = l_analogValue - g_offset;
  l_actualval = (5*l_actualval)/1024.0;
  return l_actualval * 15.5;
}

/*******************************************************************************************************
 Function Name            : loop
 Description              : Obtains the Load Status & Current sensor and push on yun bridge
 Parameters               : None
 *******************************************************************************************************/
void loop(void) {
  // put your main code here, to run repeatedly:
  long l_millisec = millis();
  long time = l_millisec / 1000;
  int l_load_data_1 = digitalRead(SWITCH_PIN_1);
  int l_load_data_2 = digitalRead(SWITCH_PIN_2);
  if(l_load_data_1 == 1){
    digitalWrite(LOAD_PIN_1,0);
  }
  else digitalWrite(LOAD_PIN_1,1);

  
  if(l_load_data_2 == 1){
    digitalWrite(LOAD_PIN_2,0);
  }
  else digitalWrite(LOAD_PIN_2,1);

  if(g_current > 0.50 || l_load_data_1 == 1 && l_load_data_2 == 1){
    digitalWrite(RELAY_PIN,1);
  }
  else if(g_current == 0.00 && l_load_data_1 == 1 || l_load_data_2 == 1){
    digitalWrite(RELAY_PIN,1);  
  }
  else digitalWrite(RELAY_PIN,0);
  
  g_current = sensor_input(CURRENT_SENSOR_1);
  if(g_current < 0.15){
    g_current = 0.00;
  }
 
  g_current_1 = sensor_input(CURRENT_SENSOR_2);
  if(g_current_1 < 0.09){
    g_current_1 = 0.00;
  }

  g_current_2 = sensor_input(CURRENT_SENSOR_3);
  if(g_current_2 < 0.09){
    g_current_2 = 0.00;
  }

  g_totamps = g_totamps + g_current;
  g_avgamps = g_totamps/time; // average amps
  g_amphr = (g_avgamps * time)/3600;  // amphour
  
  g_watt = 12 * g_current;    // power=voltage*current
  if (g_watt < 0.00) 
  {
    g_watt=0.0;
  } 
  g_energy = (g_watt * time)/3600;   //energy in watt hour
  // g_energy = (g_watt * time)/(1000*3600);   // energy in kWh
  
  g_totamps_1 = g_totamps_1 + g_current_1;
  g_avgamps_1 = g_totamps_1/time; // average amps
  g_amphr_1 = (g_avgamps_1 * time)/3600;  // amphour
  
  g_watt_1 = 12 * g_current_1;    // power=voltage*current
  if (g_watt_1 < 0.00) 
  {
    g_watt_1 = 0.0;
  } 
  g_energy_1 = (g_watt_1 * time)/3600;   //energy in watt hour
  // g_energy_1 = (g_watt_1 * time)/(1000*3600);   // energy in kWh

  g_totamps_2 = g_totamps_2 + g_current_2;
  g_avgamps_2 = g_totamps_2/time; // average amps
  g_amphr_2 = (g_avgamps_2 * time)/3600;  // amphour
  
  g_watt_2 = 12 * g_current_2;    // power=voltage*current
  if (g_watt_2 < 0.00) 
  {
    g_watt_2 = 0.0;
  } 
  g_energy_2 = (g_watt_2 * time)/3600;   //energy in watt hour
  // g_energy_2 = (g_watt_2 * time)/(1000*3600);   // energy in kWh

  String l_json_data;
  
  l_json_data = "{\"LOAD_1\":";
  l_json_data += String(l_load_data_1);
  l_json_data += ",\"LOAD_2\":";
  l_json_data += String(l_load_data_2);
  l_json_data += ",\"current_1\":";
  l_json_data += String(g_current);
  l_json_data += ",\"energy_1\":";
  l_json_data += String(g_energy);
  l_json_data += ",\"current_2\":";
  l_json_data += String(g_current_1);
  l_json_data += ",\"energy_2\":";
  l_json_data += String(g_energy_1);
  l_json_data += ",\"current_3\":";
  l_json_data += String(g_current_2);
  l_json_data += ",\"energy_3\":";
  l_json_data += String(g_energy_2);
  l_json_data += "}";

  Serial.println(l_json_data);
  Serial1.println(l_json_data);
  delay(50);
}

//End of the Program