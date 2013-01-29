#include <Servo.h>
#include <SPI.h>
#include <CmdMessenger.h>
#include <Base64.h>
#include <Streaming.h>

#define STEER_RUN 	2000
#define STEER_LUN       1000
#define STEER_TIME 	800
#define STEER_UNIT      0.1
#define STEER_INTER_1   2 //pin 21
#define STEER_INTER_2   3 //pin 20
#define STEER_INTER_G   4 //pin 19
#define STEER_PIN	9

#define BRAKE_UNIT 	1800
#define BRAKE_TIME 	500
#define BRAKE_ON_PIN    0 //pin 2
#define BRAKE_OFF_PIN   1 //pin 3
#define BRAKE_PIN	8

#define ACCEL_UNIT 	100
#define ACCEL_MIN	1000
#define ACCEL_MAX	2000
#define SLAVE_SELECT    53

#define RELAY_ACCEL     32
#define RELAY_POWER     31
#define RELAY_RAM       33
#define RELAY_DIRECTION 30

#define BAUD_RATE	115200

Servo steer;
Servo brake;

int readSpeed;
volatile double steeringAngle;
volatile boolean inter_1_state;
volatile boolean inter_2_state;
volatile boolean inter_g_state;
int steerSetAngle;
boolean forwardDirection = true;
volatile boolean brake_state = false;
int brakeSetTime;
int time;
int buf;
int intbuf;
int i = 0;
int currentSpeed = 0;


// Mustnt conflict / collide with our message payload data. Fine if we use base64 library ^^ above
char field_separator = ',';
char command_separator = ';';
CmdMessenger cmdMessenger = CmdMessenger(Serial, field_separator, command_separator);

enum
{
  kCOMM_ERROR    = 000, // Lets Arduino report serial port comm error back to the PC (only works for some comm errors)
  kACK           = 001, // Arduino acknowledges cmd was received
  kARDUINO_READY = 002, // After opening the comm port, send this cmd 02 from PC to check arduino is ready
  kERR           = 003, // Arduino reports badly formatted cmd, or cmd not recognised

  // Now we can define many more 'send' commands, coming from the arduino -> the PC, eg
  // kICE_CREAM_READY,
  // kICE_CREAM_PRICE,
  // For the above commands, we just call cmdMessenger.sendCmd() anywhere we want in our Arduino program.

  kSEND_CMDS_END, // Mustnt delete this line
};

// Commands we send from the PC and want to recieve on the Arduino.
// We must define a callback function in our Arduino program for each entry in the list below vv.
// They start at the address kSEND_CMDS_END defined ^^ above as 004
messengerCallbackFunction messengerCallbacks[] = 
{
  Steering,     // 004 
  Accelerate,  // 005
  Stop,         // 006
  //switchDirection, //007
  NULL
};

void arduino_ready()
{
  // In response to ping. We just send a throw-away Acknowledgement to say "im alive"
  cmdMessenger.sendCmd(kACK,"Arduino ready");
}

void unknownCmd()
{
  // Default response for unknown commands and corrupt messages
  cmdMessenger.sendCmd(kERR,"Unknown command");
}

void attach_callbacks(messengerCallbackFunction* callbacks)
{
  int i = 0;
  int offset = kSEND_CMDS_END;
  while(callbacks[i])
  {
    cmdMessenger.attach(offset+i, callbacks[i]);
    i++;
  }
}

/************************************************************/
// Steering fucntions 

void steerPulse()
{
  if(steeringAngle >= steerSetAngle)
  {
    stopSteering();
  }
  setTime();
}

void stopSteering()
{
  steer.writeMicroseconds(1500);
}

//steer_inter_1 is called when ever the opical encoder inits a interupt
// that is defined in the Setup(). When the 1 wire wiggles steer_inter_1
// checks the statis of the 2 wire to deturmine the direction the wheel is 
// turning and sets steeringAngle plus or minus the STEER_UNIT accordingly
void steer_inter_1()
{
  inter_1_state = !inter_1_state;
  if (inter_2_state)
  {
    if(inter_1_state)
      steeringAngle = steeringAngle - STEER_UNIT;
    else
      steeringAngle = steeringAngle + STEER_UNIT;
  }
  else
  {
    if(inter_1_state)
      steeringAngle = steeringAngle + STEER_UNIT;
    else
      steeringAngle = steeringAngle - STEER_UNIT;
  }    
}   

void steer_inter_2()
{
  inter_2_state = !inter_2_state;
  if (inter_1_state)
  {
    if(inter_2_state)
      steeringAngle = steeringAngle + STEER_UNIT;
    else
      steeringAngle = steeringAngle - STEER_UNIT;
  }
  else
  {
    if(inter_1_state)
      steeringAngle = steeringAngle - STEER_UNIT;
    else
      steeringAngle = steeringAngle + STEER_UNIT;
  }    
}   

void Steering()
{
  while( cmdMessenger.available())
  {    
    buf = cmdMessenger.readInt();
  }
  cmdMessenger.sendCmd(kACK,"I got Steer");
  intbuf = buf & 0x7FFF;
  //intbuf = buf & 127255;      //B01111111111111111
  //steerSetTime = STEER_TIME + time;
  steerSetAngle = intbuf;
  
  if (steeringAngle > buf)
  {
    steer.write(2000);
    //delay(1250);
    //moveSteering(false);
    cmdMessenger.sendCmd(kACK,"I got left");
  }
  else if (steeringAngle < buf)
  {
    steer.write(1000);
    //moveSteering(true);
    cmdMessenger.sendCmd(kACK,"I got right");
  }
  //steeringAngle = intbuf;
}

/************************************************************/
//Acceleration fucntions 
// Accerlerate gets called by CmdMessenger and reads an int value 
// to set the acceleration to. It calls formatDACommand to 
// ensure a correctly formated value is passed to the DAC

void switchDirection(boolean forward)
{
//  while( cmdMessenger.available())
//  {    
//    buf = cmdMessenger.readInt();
//  }
  if(forward)
  {
    stopAccel();
    forwardDirection = true;
    digitalWrite(RELAY_DIRECTION,HIGH);
  }
  else
  {
    stopAccel();
    forwardDirection = false;
    digitalWrite(RELAY_DIRECTION,LOW);
  }
}

unsigned int formatDACommand(unsigned int value)
{
  value = value<<1;
  value = value & 8190;          //B0001111111111110
  return value;
}

void setAccel(unsigned int value)
{
  //currentForwardSpeed += value;
  
  value = formatDACommand(value);
  digitalWrite(SLAVE_SELECT,LOW);
  SPI.transfer(value>>8);
  SPI.transfer(value);
  digitalWrite(SLAVE_SELECT,HIGH); 
}

void stopAccel()
{
  readSpeed = readSpeed & 0;
  currentSpeed = 0;
  setAccel(0);
}

void Accelerate()
{
  while( cmdMessenger.available())
  {    
    buf = cmdMessenger.readInt();
  }
  cmdMessenger.sendCmd(kACK,"I got Accel");
  if(buf < 0 && forwardDirection == true)
  {
    switchDirection(false);
    setAccel(-buf);
  }
  else if (buf > 0 && forwardDirection == false)
  {
    switchDirection(true);
    setAccel(buf);
  }
  else
	setAccel(abs(buf));
}

/************************************************************/
//Stop fucntions 

void Stop()
{
  cmdMessenger.sendCmd(kACK,"I got Stop");
  stopAll();
}

void stopAll()
{
  stopAccel();
  stopSteering();
  if(!brake_state)
    applyBrake();
}

void brakeState()
{
  brake_state = !brake_state;
  stopBrake();
}

void stopBrake()
{
  brake.write(1500);
}

// Call applyBrake() to start the brake motor braking
// the interupt function stopBrake() will stop the motor
// when the switch on either end goes from low to high
// To release brake call applyBrake() again. 
void applyBrake()
{
  if(brake_state)
    brake.write(1000);
  else
    brake.write(2000);
}

/************************************************************/
//Time fucntions 

void setTime()
{
  time = millis();
}

/************************************************************/
//The Setup

void setup()
{
  Serial.begin(BAUD_RATE);
  
  cmdMessenger.print_LF_CR(); //more readable comment out for real
  cmdMessenger.attach(kARDUINO_READY, arduino_ready);
  cmdMessenger.attach(unknownCmd);
  attach_callbacks(messengerCallbacks);
  arduino_ready();
  
  setTime();  
  
  //Inits the Accerator stuff to change speed or resistance on the 
  // maxim chip
  pinMode(SLAVE_SELECT, OUTPUT);
  SPI.setDataMode(SPI_MODE0);
  SPI.setClockDivider(SPI_CLOCK_DIV2);
  SPI.setBitOrder(MSBFIRST);
  SPI.begin();

  attachInterrupt(STEER_INTER_1, steer_inter_1, CHANGE); 
  attachInterrupt(STEER_INTER_2, steer_inter_2, CHANGE);
  attachInterrupt(STEER_INTER_G, steer_inter_180, RISING);
  steer.attach(STEER_PIN);
  steeringAngle = 0.0;
  
  attachInterrupt(BRAKE_ON_PIN, brakeState, RISING);
  attachInterrupt(BRAKE_OFF_PIN, brakeState, RISING);
  brake.attach(BRAKE_PIN);
  
  steer.writeMicroseconds(1500);
  brake.writeMicroseconds(1500);
  
  pinMode(RELAY_ACCEL,OUTPUT);
  //pinMode(RELAY_STEER,OUTPUT);
  pinMode(RELAY_POWER,OUTPUT);
  //pinMode(RELAY_RAM,OUTPUT);
  pinMode(RELAY_DIRECTION,OUTPUT);
  
  digitalWrite(RELAY_ACCEL,LOW);
  //digitalWrite(RELAY_STEER,LOW);
  digitalWrite(RELAY_POWER,LOW);
  //digitalWrite(RELAY_RAM,LOW);
  digitalWrite(RELAY_DIRECTION,HIGH);
}

void loop()
{
  cmdMessenger.feedinSerialData();
  steerPulse();
  brakePulse();
}




