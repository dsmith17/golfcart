#include <Servo.h>
#include <SPI.h>
#include <CmdMessenger.h>
#include <Base64.h>
#include <Streaming.h>

#define STEER_R_SPEED 	1100
#define STEER_L_SPEED   1900
#define STEER_TIME 	800
#define STEER_UNIT      0.036/2 // the model#  360/10000
#define STEER_INTER_1   4 //pin 19
#define STEER_PIN_1     19
#define STEER_INTER_2   5 //pin 18
#define STEER_PIN_2     18
#define STEER_INTER_G   3 //pin 20
#define STEER_PIN	9
#define STEER_ACTIVE    true
#define DEGREE_PREC     1
#define DEGREE_DELTA    3

#define BRAKE_UNIT 	1800
#define BRAKE_TIME 	500
#define BRAKE_ON_PIN    38 //pin 2
#define BRAKE_OFF_PIN   39 //pin 3
#define BRAKE_PIN	8
#define BRAKE_RELEASE   1000
#define BRAKE_APPLY     2000

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
volatile boolean activeSteer = true;
volatile int steerState = 0; // 1=left, 0=stop, -1=right
double steerSetAngle;
boolean forwardDirection = true;
volatile int brake_status = 0; // 0=release, 1=applying, 2=not moving
int brake_on_state;
int brake_off_state;
volatile boolean brake_set = false;
int brakeSetTime;
int time;
int buf;
int intbuf;
int i = 0;
int currentSpeed = 0;
char response_buff[50];
int printnow = 0;
double setAngle = 0;
double curAngle = 0;

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
  kDIRECTION     = 7,
  kSTEERMODE     = 8,
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
  //setAngle = steerSetAngle & 0x7FFF;
  //curAngle = steeringAngle & 0x7FFF;
  
  if(steeringAngle < 0)
    curAngle = steeringAngle * -1;
  else
    curAngle = steeringAngle;
    
  if(steerSetAngle < 0)
    setAngle = steerSetAngle * -1;
  else
    setAngle = steerSetAngle;
  
  if(activeSteer)
  {
    if(steerState == -1) //turning right
    {
      if(steeringAngle >= steerSetAngle)
      {
        steerState = 0;
        //Serial.println("Stopping right");
        //Serial.println(steeringAngle);
        stopSteering();        
      }
      else if(steeringAngle < (steerSetAngle - DEGREE_PREC) && (setAngle - curAngle) < DEGREE_DELTA)
      {
        //Serial.println("Im slowing right");
        steer.writeMicroseconds(1200);
        //steer.writeMicroseconds(1800 + ((steeringAngle + steerSetAngle)/DEGREE_DELTA)*100);
        
      }
    }
    else if(steerState == 1) //turning left
    {
      if(steeringAngle <= steerSetAngle)
      {
        steerState = 0;
        //Serial.println("Stopping left");
        //Serial.println(steeringAngle);
        stopSteering();
      }
      else if(steeringAngle > (steerSetAngle + DEGREE_PREC) && (curAngle - setAngle) < DEGREE_DELTA)
      {
        //Serial.println("Im slowing left");
        steer.writeMicroseconds(1800);
        //steer.writeMicroseconds(1200 - ((steeringAngle - steerSetAngle)/DEGREE_DELTA)*100);
      }
    }
    else if(steeringAngle < (steerSetAngle - DEGREE_PREC))
    {
      //Serial.println("Starting right");
      //Serial.println(steeringAngle);
      steerState = -1;
      steer.writeMicroseconds(STEER_R_SPEED);
    }
    else if(steeringAngle > (steerSetAngle + DEGREE_PREC))
    {
      //Serial.println("Starting left");
      //Serial.println(steeringAngle);
      steerState = 1;
      steer.writeMicroseconds(STEER_L_SPEED);
    }
  }
      
      
//    if(steeringAngle >= (steerSetAngle - DEGREE_PREC) || steeringAngle <= (steerSetAngle + DEGREE_PREC)) 
//    {
//      stopSteering();
//    }
//    else if(steeringAngle > (steerSetAngle + DEGREE_PREC) && (steeringAngle - steerSetAngle) < DEGREE_DELTA)
//    {
//      steer.writeMicroseconds(1300 - ((steeringAngle - steerSetAngle)/DEGREE_DELTA)*200);
//    }
//    else if(steeringAngle < (steerSetAngle - DEGREE_PREC/2) && (steerSetAngle - steeringAngle) < DEGREE_DELTA)
//    {
//      steer.writeMicroseconds(1500 - ((steeringAngle - steerSetAngle)/DEGREE_DELTA)*400);
//    }
//    else if(steeringAngle < (steerSetAngle - DEGREE_PREC/2))
//    {
//      steer.writeMicroseconds(STEER_RUN);
//    }
//    else if(steeringAngle > (steerSetAngle + DEGREE_PREC/2))
//    {
//      steer.writeMicroseconds(STEER_LUN);
//    }

  else
  {
    if(steerState == -1) // -1 is right
    {
      if(steeringAngle >= steerSetAngle)
      {
        //Serial.println("Stopping Right Turn");
        //Serial.println(steeringAngle);
        stopSteering();
        steerState = 0;
      }
    }
    else if(steerState == 1) // 1 is left
    {
      if(steeringAngle <= steerSetAngle)
      {
        //Serial.println("Stopping Left Turn");
        //Serial.println(steeringAngle);
        stopSteering();
        steerState = 0;
      }
    }
  }
  setTime();
  if(printnow == 1)
  {
    //Serial.println(steeringAngle);
    printnow = 0;
  }
}

void stopSteering()
{
  steer.writeMicroseconds(1500);
//  Serial.println("I am Stopping");
}

// When in active steer state the steering will try and keep the set angle
void setActiveSteer()
{
  activeSteer = 1;
}

// When in Passive state the steering will set the steering angle then 
// release control
void setPassiveSteer()
{
  activeSteer = 0;
}

//steer_inter_1 is called when ever the opical encoder inits a interupt
// that is defined in the Setup(). When the 1 wire wiggles steer_inter_1
// checks the statis of the 2 wire to deturmine the direction the wheel is 
// turning and sets steeringAngle plus or minus the STEER_UNIT accordingly
void steer_inter_1()
{
  inter_1_state = digitalRead(STEER_PIN_1);
  inter_2_state = digitalRead(STEER_PIN_2);
  if (inter_2_state)
  {
    if(inter_1_state)
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
//  printnow = 1;
//  cmdMessenger.sendCmd(kACK,);
//  Serial.println(steeringAngle);
}   

void steer_inter_2()
{
  inter_1_state = digitalRead(STEER_PIN_1);
  inter_2_state = digitalRead(STEER_PIN_2);
  if (inter_1_state)
  {
    if(inter_2_state)
      steeringAngle = steeringAngle - STEER_UNIT;
    else
      steeringAngle = steeringAngle + STEER_UNIT;
  }
  else
  {
    if(inter_2_state)
      steeringAngle = steeringAngle + STEER_UNIT;
    else
      steeringAngle = steeringAngle - STEER_UNIT;
  }
  //cmdMessenger.sendCmd(kACK,"The steer angle is: %d",steeringAngle);
}   

void steerMode()
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
  cmdMessenger.sendCmd(kSTEERMODE,response_buff);
  
  if(val == 0)
    activeSteer = true;
  else if(val = 1)
    activeSteer = false;
}

void Steering()
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
  cmdMessenger.sendCmd(kSTEERING,response_buff);
  
  //intbuf = buf & 0x7FFF;
  //intbuf = buf & 127255;      //B01111111111111111
  //steerSetTime = STEER_TIME + time;
  steerSetAngle = val;
  
  if (steeringAngle > buf)
  {
    steer.write(1900);
    //delay(1250);
    //moveSteering(false);
    steerState = 1;
    //cmdMessenger.sendCmd(kACK,"I got left");
  }
  else if (steeringAngle < buf)
  {
    steer.write(1100);
    //moveSteering(true);
    steerState = -1;
    //cmdMessenger.sendCmd(kACK,"I got right");
  }
  //steeringAngle = intbuf;
}

/************************************************************/
//Acceleration fucntions 
// Accerlerate gets called by CmdMessenger and reads an int value 
// to set the acceleration to. It calls formatDACommand to 
// ensure a correctly formated value is passed to the DAC

//The raspberry pi is responsible for stopping the golf cart
// before the switchDirection function is called.
void SwitchDirection()
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
  cmdMessenger.sendCmd(kDIRECTION,response_buff);
  
  if(val == 0)
  {
    stopAccel();
    forwardDirection = true;
    digitalWrite(RELAY_DIRECTION,HIGH);
  }
  else if(val == 1)
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
//  if(val < 0 && forwardDirection == true)
//  {
//    switchDirection(false);
//    setAccel(-val);
//  }
//  else if (val > 0 && forwardDirection == false)
//  {
//    switchDirection(true);
//    setAccel(val);
//  }
//  else
  currentSpeed = val;
  setAccel(abs(val));
}

/************************************************************/
//Stop fucntions 

void Stop()
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
  
  if(val == 1)
    applyBrake();
  else
    releaseBrake();
    
  //cmdMessenger.sendCmd(kACK,"I got Stop");
  //stopAll();
}

void stopAll()
{
  stopAccel();
  stopSteering();
  applyBrake();
}

// Call applyBrake() to start the brake motor braking
// the interupt function stopBrake() will stop the motor
// when the switch on either end goes from low to high 
void applyBrake()
{
  brake.writeMicroseconds(BRAKE_APPLY);
  brake_status = 1; // 1 = the brake is being applied
}

void releaseBrake()
{
  brake.writeMicroseconds(BRAKE_RELEASE);
  brake_status = 0; // 0 = the brake is being released
}

void brakePulse()
{
  brake_on_state = digitalRead(BRAKE_ON_PIN);
  brake_off_state = digitalRead(BRAKE_OFF_PIN);
  
  if(brake_off_state == 1 && brake_status == 0)
  {
    brake.writeMicroseconds(1500);
    brake_set = true;
    brake_status = 2;
  }
  else if(brake_on_state == 1 && brake_status == 1)
  {
    brake.writeMicroseconds(1500);
    brake_set = true;
    brake_status = 2;
  }   
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
         seq, (int)steeringAngle, currentSpeed, dir, brake_status, 0);
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
  cmdMessenger.attach(kSTEERMODE, steerMode);
  cmdMessenger.attach(kSTOP,     Stop);
  cmdMessenger.attach(kDIRECTION, SwitchDirection);
  cmdMessenger.attach(kACCEL,    Accelerate);  
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
  
  //attachInterrupt(BRAKE_ON_PIN, brakeInterupt, RISING);
  //attachInterrupt(BRAKE_OFF_PIN, brakeInterupt, RISING);
  pinMode(BRAKE_ON_PIN, INPUT_PULLUP);
  pinMode(BRAKE_OFF_PIN, INPUT_PULLUP);  
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
  brakePulse();
}




