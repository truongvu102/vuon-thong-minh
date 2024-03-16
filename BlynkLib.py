import BlynkLib
import RPi.GPIO as GPIO
from BlynkTimer import BlynkTimer
import Adafruit_DHT
import time


GPIO.setmode(GPIO.BCM)
BLYNK_AUTH_TOKEN = 'SBR6vGNZ0vu0Ln68IY748SfPl91c3nlT'

dout_pin = 18
GPIO.setup(dout_pin, GPIO.IN)

led1 = 14
led2 = 15
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)


servo_pin = 17
GPIO.setup(servo_pin, GPIO.OUT)
servo_pwm = GPIO.PWM(servo_pin, 50)  

blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN)


moisture_timer = BlynkTimer()
dht_timer = BlynkTimer()


temperature = 0
humidity = 0


v6_state = 0

def read_moisture():
    moisture_value = GPIO.input(dout_pin)

    if moisture_value == 0:
        print("Đất ẩm")
        blynk.virtual_write(4, 1)  
    else:
        print("Đất khô")
        blynk.virtual_write(4, 0)  

    if v6_state and temperature is not None:  
        if temperature > 33:  
            GPIO.output(led1, GPIO.HIGH)  
            blynk.virtual_write(2, 1)
        elif temperature <= 33:
            GPIO.output(led1, GPIO.LOW)  
            blynk.virtual_write(2, 0)
    else:
        GPIO.output(led1, GPIO.LOW)  
        blynk.virtual_write(2, 0)
    
    if v6_state and humidity is not None:
        if humidity > 75: 
            GPIO.output(led2, GPIO.HIGH)  
            blynk.virtual_write(3, 1)
        elif humidity < 75:
            GPIO.output(led2, GPIO.LOW)  
            blynk.virtual_write(3, 0)
    else:
        GPIO.output(led2, GPIO.LOW)  
        blynk.virtual_write(3, 0)
        
    if v6_state:
        if moisture_value == 1:
            servo_pwm.start(7.5)  
            time.sleep(1)
            blynk.virtual_write(5, 1)  
        else:
            servo_pwm.start(2.5)  
            time.sleep(1)
            blynk.virtual_write(5, 0)  
        

def read_dht():
    global temperature, humidity
    humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT11, 4)
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
	blynk.virtual_write(0, humidity)
        blynk.virtual_write(1, temperature)
    else:
        print("Sensor failure. Check wiring.")



@blynk.on("V6")
def v6_write_handler(value):
    global v6_state
    if int(value[0]) != 0:
        v6_state = 1
        print("bat che do tu dong")
    else:
        v6_state = 0
        print("tat che do tu dong")

@blynk.on("V2")
def v2_write_handler(value):
    if int(value[0]) != 0:
        GPIO.output(led1, GPIO.HIGH)
        print('LED1 Bat')
    else:
        GPIO.output(led1, GPIO.LOW)
        print('LED1 Tat')


@blynk.on("V3")
def v3_write_handler(value):
    if int(value[0]) != 0:
        GPIO.output(led2, GPIO.HIGH)
        print('LED2 bat')
    else:
        GPIO.output(led2, GPIO.LOW)
        print('LED2 tat')
@blynk.on("V5")
def v5_write_handler(value):
    if int(value[0]) != 0:
        
        servo_pwm.start(7.5)  
        time.sleep(1)
    else:
        
        servo_pwm.start(2.5)  
        time.sleep(1)


@blynk.on("connected")
def blynk_connected():
    print("Raspberry Pi Connected to New Blynk")


moisture_timer.set_interval(5, read_moisture)
dht_timer.set_interval(2, read_dht)

while True:
    blynk.run()
    moisture_timer.run()
    dht_timer.run()
