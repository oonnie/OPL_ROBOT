import time
import serial
from RPIO import PWM
from flask import Flask, render_template, request

app = Flask (__name__, static_url_path = '')

# Connect to the comm port to talk to the Roboclaw motor controller
try:
   # Change the baud rate here if diffrent than 19200
   roboclaw = serial.Serial ('/dev/ttyAMA0', 19200)
except IOError:
   print ("Comm port not found")
   sys.exit (0)

# Speed and drive control variables
last_direction = -1
speed_offset = 84
turn_tm_offset = 0.166
run_time = 0.750

# Servo neutral position (home)
servo_pos = 1250
servo = PWM.Servo ( )
servo.set_servo (18, servo_pos)

# A little dwell for settling down time
time.sleep (3)

#
# URI handlers - all the bot page actions are done here
#

# Send out the bots control page (home page)
@app.route ("/")
def index ( ):
   return render_template ('index.html', name = None)

@app.route ("/forward")
def forward ( ):
   global last_direction, run_time

   print "Forward"
   go_forward ( )
   last_direction = 0

   # sleep 100ms + run_time
   time.sleep (0.100 + run_time)

   # If not continuous, then halt after delay
   if run_time > 0:
      last_direction = -1
      halt ( )

   return "ok"

@app.route ("/backward")
def backward ( ):
   global last_direction, run_time

   print "Backward"
   go_backward ( )
   last_direction = 1

   # sleep 100ms + run_time
   time.sleep (0.100 + run_time)

   # If not continuous, then halt after delay
   if run_time > 0:
      last_direction = -1
      halt ( )

   return "ok"

@app.route ("/left")
def left ( ):
   global last_direction, turn_tm_offset

   print "Left"
   go_left ( )
   last_direction = -1

   # sleep @1/2 second
   time.sleep (0.500 - turn_tm_offset)

   # stop
   halt ( )
   time.sleep (0.100)
   return "ok"

@app.route ("/right")
def right ( ):
   global last_direction, turn_tm_offset

   print "Right"
   go_right ( )

   # sleep @1/2 second
   time.sleep (0.500 - turn_tm_offset)
   last_direction = -1

   # stop
   halt ( )
   time.sleep (0.100)
   return "ok"

@app.route ("/ltforward")
def ltforward ( ):
   global last_direction, turn_tm_offset

   print "Left forward turn"
   go_left ( )

   # sleep @1/8 second
   time.sleep (0.250 - (turn_tm_offset / 2))
   last_direction = -1

   # stop
   halt ( )
   time.sleep (0.100)
   return "ok"

@app.route ("/rtforward")
def rtforward ( ):
   global last_direction, turn_tm_offset

   print "Right forward turn"
   go_right ( )

   # sleep @1/8 second
   time.sleep (0.250 - (turn_tm_offset / 2))
   last_direction = -1

   # stop
   halt ( )
   time.sleep (0.100)
   return "ok"

@app.route ("/stop")
def stop ( ):
   global last_direction

   print "Stop"
   halt ( )
   last_direction = -1

   # sleep 100ms
   time.sleep (0.100)
   return "ok"

@app.route ("/panlt")
def panlf ( ):
   global servo_pos

   print "Panlt"
   servo_pos -= 100
   if servo_pos < 500:
      servo_pos = 500

   servo.set_servo (18, servo_pos)

   # sleep 150ms
   time.sleep (0.150)
   return "ok"

@app.route ("/panrt")
def panrt ( ):
   global servo_pos

   print "Panrt"
   servo_pos += 100
   if servo_pos > 2500:
      servo_pos = 2500

   servo.set_servo (18, servo_pos)

   # sleep 150ms
   time.sleep (0.150)
   return "ok"

@app.route ("/home")
def home ( ):
   global servo_pos

   print "Home"
   servo_pos = 1250

   servo.set_servo (18, servo_pos)

   # sleep 150ms
   time.sleep (0.150)
   return "ok"

@app.route ("/panfull_lt")
def panfull_lt ( ):
   global servo_pos

   print "Pan full left"
   servo_pos = 500

   servo.set_servo (18, servo_pos)

   # sleep 150ms
   time.sleep (0.150)
   return "ok"

@app.route ("/panfull_rt")
def panfull_rt ( ):
   global servo_pos

   print "Pan full right"
   servo_pos = 2500

   servo.set_servo (18, servo_pos)

   # sleep 150ms
   time.sleep (0.150)
   return "ok"

@app.route ("/speed_low")
def speed_low ( ):
   global speed_offset, last_direction, turn_tm_offset

   speed_offset = 42
   turn_tm_offset = 0.001

   # Update current direction to get new speed
   if last_direction == 0:
       go_forward ( )
   if last_direction == 1:
       go_backward ( )

   # sleep 150ms
   time.sleep (0.150)
   return "ok"

@app.route ("/speed_mid")
def speed_mid ( ):
   global speed_offset, last_direction, turn_tm_offset

   speed_offset = 84
   turn_tm_offset = 0.166

   # Update current direction to get new speed
   if last_direction == 0:
       go_forward ( )
   if last_direction == 1:
       go_backward ( )

   # sleep 150ms
   time.sleep (0.150)
   return "ok"

@app.route ("/speed_hi")
def speed_hi ( ):
   global speed_offset, last_direction, turn_tm_offset

   speed_offset = 126
   turn_tm_offset = 0.332

   # Update current direction to get new speed
   if last_direction == 0:
       go_forward ( )
   if last_direction == 1:
       go_backward ( )

   # sleep 150ms
   time.sleep (0.150)
   return "ok"

@app.route ("/continuous")
def continuous ( ):
   global run_time

   print "Continuous run"
   run_time = 0

   # sleep 100ms
   time.sleep (0.100)
   return "ok"

@app.route ("/mid_run")
def mid_run ( ):
   global run_time

   print "Mid run"
   run_time = 0.750
   halt ( )

   # sleep 100ms
   time.sleep (0.100)
   return "ok"

@app.route ("/short_time")
def short_time ( ):
   global run_time

   print "Short run"
   run_time = 0.300
   halt ( )

   # sleep 100ms
   time.sleep (0.100)
   return "ok"

#
# Motor drive functions
#
def go_forward ( ):
    global speed_offset

    if speed_offset != 42:
        roboclaw.write (chr (1 + speed_offset))
        roboclaw.write (chr (128 + speed_offset))
    else:
        roboclaw.write (chr (127 - speed_offset))
        roboclaw.write (chr (255 - speed_offset))

def go_backward ( ):
    global speed_offset

    if speed_offset != 42:
        roboclaw.write (chr (127 - speed_offset))
        roboclaw.write (chr (255 - speed_offset))
    else:
        roboclaw.write (chr (1 + speed_offset))
        roboclaw.write (chr (128 + speed_offset))

def go_left ( ):
    global speed_offset

    if speed_offset != 42:
        roboclaw.write (chr (127 - speed_offset))
        roboclaw.write (chr (128 + speed_offset))
    else:
        roboclaw.write (chr (1 + speed_offset))
        roboclaw.write (chr (255 - speed_offset))

def go_right ( ):
    global speed_offset

    if speed_offset != 42:
        roboclaw.write (chr (1 + speed_offset))
        roboclaw.write (chr (255 - speed_offset))
    else:
        roboclaw.write (chr (127 - speed_offset))
        roboclaw.write (chr (128 + speed_offset))

def halt ( ):
    roboclaw.write (chr (0))

if __name__ == "__main__" :
   app.run (host = '0.0.0.0', port = 80, debug = True)
