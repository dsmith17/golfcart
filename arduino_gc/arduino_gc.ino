#include <Servo.h>
#include <SPI.h>
#include <CmdMessenger.h>
#include <Base64.h>
#include <Streaming.h>

#define STEER_RUN 	2000
#define STEER_LUN       1000
#define STEER_TIME 	800
#define STEER_UNIT      0.36 // the model#  360/1000
#define STEER_INTER_1   4 //pin 21
#define STEER_PIN_1     19
#define STEER_INTER_2   5 //pin 20
#define STEER_PIN_2     18
#define STEER_INTER_G   4 //pin 19
#define STEER_PIN	9
#define STEER_ACTIVE    true
#define DEGREE_PREC     5
#define DEGREE_DELTA    10

#define BRAKE_UNIT 	1800
#define BRAKE_TIME 	500
#define BRAKE_ON_PIN    30 //pin 2
#define BRAKE_OFF_PIN   31 //pin 3
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
char response_buff[50];

// Mustnt conflict / collide with our message payload data. Fine if we use base64 library ^^ above
char field_separator = ',';
char command_separator = ';';
CmdMessenger cmdMessenger = CmdMessenger(Serial, field_separator, command_separator);

enum
{
  kCOMM_ERROR    = 0, // Lets Arduino report serial port comm error back to the PC (only works for some comm errors)
  kACK           = 1, // Arduino acknowledges cmd was received
  kARDUINO_READY = 2, // After opening the comm port, send this cmd 02 from PC to check arduino is ready
  kERR           = 3, // Arduino reports badly formatted cmd, or cmd not recognised

  // Now we can define many more 'send' commands, coming from the arduino -> the PC, eg
  kSTEERING      = 4,
  kACCEL         = 5,
  kSTOP          = 6,
  kSTATUS        = 9,
  // For the above commands, we just call cmdMessenger.sendCmd() anywhere we want in our Arduino program.

  kSEND_CMDS_END, // Mustnt delete this line
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
#ifdef STEER_ACTIVE
  if(steeringAngle >= (steerSetAngle - DEGREE_PREC/2) || steeringAngle <= (steerSetAngle + DEGREE_PREC/2)) 
  {
    stopSteering();
  }
  else if(steeringAngle > (steerSetAngle + DEGREE_PREC/2) && (steeringAngle - steerSetAngle) < DEGREE_DELTA)
  {
    steer.writeMicroseconds(1400 - ((steeringAngle - steerSetAngle)/DEGREE_DELTA)*400);
  }
  else if(steeringAngle < (steerSetAngle - DEGREE_PREC/2) && (steerSetAngle - steeringAngle) < DEGREE_DELTA)
  {
    steer.writeMicroseconds(1400 - ((steeringAngle - steerSetAngle)/DEGREE_DELTA)*400);
  }
  else if(steeringAngle < (steerSetAngle - DEGREE_PREC/2))
  {
    steer.writeMicroseconds(STEER_RUN);
  }
  else if(steeringAngle > (steerSetAngle + DEGREE_PREC/2))
  {
    steer.writeMicroseconds(STEER_LUN);
  }
#else
  if(steeringAngle >= steerSetAngle)
  {
    stopSteering();
  }
#endif
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
  inter_1_state = digitalRead(STEER_PIN_1);
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
 
//  cmdMessenger.sendCmd(kACK,);  
}   

void steer_inter_2()
{
  inter_2_state = digitalRead(STEER_PIN_2);
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
  //cmdMessenger.sendCmd(kACK,"The steer angle is: %d",steeringAngle);
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
  int seq, val;
  
  seq = cmdMessenger.readInt();
  if (cmdMessenger.available())
     val = cmdMessenger.readInt();
  else
  {
    cmdMessenger.sendCmd(kACK, "Invalid command");
    return;
  }
  
  sprintf(response_buff, "%d,0", seq);
  cmdMessenger.sendCmd(kACCEL,response_buff);
  if(val < 0 && forwardDirection == true)
  {
    switchDirection(false);
    setAccel(-val);
  }
  else if (val > 0 && forwardDirection == false)
  {
    switchDirection(true);
    setAccel(val);
  }
  else
    setAccel(abs(val));
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

//void brakePoll()
//{
  

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
    brake.write(2000);
  else
    brake.write(1000);
}

void Status()
{
  int seq;
  int dir;
  
  if (cmdMessenger.available())
     seq = cmdMessenger.readInt();
  else
  {
    cmdMessenger.sendCmd(kACK, "Invalid command");
    return;
  }
  
  if (forwardDirection)
     dir = 0;
  else
     dir = 1;
     
  sprintf(response_buff, "%d,%d,%d,%d,%d,%d,0", 
         seq, steerSetAngle, currentSpeed, dir, brake_state, 0);
  cmdMessenger.sendCmd(kSTATUS,response_buff);
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
  cmdMessenger.attach(kSTEERING, Steering);
  cmdMessenger.attach(kACCEL,    Accelerate);
  cmdMessenger.attach(kSTOP,     Stop);
  cmdMessenger.attach(kSTATUS,   Status);
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
//  attachInterrupt(STEER_INTER_G, steer_inter_180, RISING);
  steer.attach(STEER_PIN);
  steeringAngle = 0.0;
  
  //attachInterrupt(BRAKE_ON_PIN, brakeState, RISING);
  //attachInterrupt(BRAKE_OFF_PIN, brakeState, RISING);
  
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
  
//  applyBrake();
//  delay(1000);
//  stopBrake();
//  brake_state = !brake_state;
//  applyBrake();
//  delay(1000);
//  stopBrake();
}

void loop()
{
  cmdMessenger.feedinSerialData();
  steerPulse();
//  brakePulse();
}




