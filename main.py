from servo import Servo
from ssd1306 import SSD1306_I2C
import time, machine
import network, time, ntptime, utime
from machine import I2C, PWM

# led = machine.Pin(2, machine.Pin.OUT)
# # motor = Servo(pin=21)

buzzer = PWM(machine.Pin(15))
i2c = I2C(0,sda = machine.Pin(2),scl = machine.Pin(5),freq = 40000)
oled = SSD1306_I2C(128, 64, i2c)

buzzer.duty_u16(0)

TIMEZONE_OFFSET = -5 

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def wifi_connect(network_name, password):
    global my_network
    
    my_network = network.WLAN(network.STA_IF)
    
    if not my_network.isconnected():
        my_network.active(True)
        my_network.connect(network_name, password)
        
        oled.fill(0)
        oled.text(f'Hello!', 42, 30, 1)
        oled.show()
        time.sleep(1)
        oled.fill(0)
        oled.text(f'Trying to', 0, 30, 1)
        oled.text(f'connect...', 0, 40, 1)
        oled.text(f'{network_name}', 0, 52, 1)
        oled.show()
        
        timeout = time.time()
        
        while not my_network.isconnected():
            if (time.ticks_diff(time.time(), timeout) > 10):
                return False
            
    return True
  
def localtime_adjusted():

    utc_time = utime.localtime()
    year, month, day, hour, minute, second, weekday, dayinyear = utc_time

    hour += TIMEZONE_OFFSET
    if hour < 0:
        hour += 24
        day -= 1
        weekday = (weekday - 1) % 7  
    elif hour >= 24: 
        hour -= 24
        day += 1
        weekday = (weekday + 1) % 7 

    days_in_month = [31, 28 + (1 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 0),
                     31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if day < 1:
        month -= 1
        if month < 1: 
            month = 12
            year -= 1
        day = days_in_month[month - 1]
    elif day > days_in_month[month - 1]:
        day = 1
        month += 1
        if month > 12:
            month = 1
            year += 1

    return year, month, day, hour, minute, second, weekday

if wifi_connect('EYE3 2.4G','Castellanos2023Ort'):
    oled.fill(0)
    oled.text('Connected!', 23, 30, 1)
    oled.show()
    time.sleep(0.5)
    
    try:
        ntptime.host = "pool.ntp.org"  
        ntptime.settime()
        print("Hour synchronized with NTP server")
    except Exception as e:
        print("Failed", e)
        
    while True:
        year, month, day, hour, minute, second, weekday = localtime_adjusted()
        
        day_name = DAYS_OF_WEEK[weekday]
        
        if (minute == 20 or minute == 40) and second == 0:
            oled.fill(1)
            oled.show()
            time.sleep(0.5)
            oled.fill(0)
            oled.show()
            
        if(minute == 59 and second == 59):
            buzzer.duty_u16(32767)
            buzzer.freq(1319)
            time.sleep(0.5)
            buzzer.duty_u16(0)

        oled.fill(0)
        oled.text(day_name, 0, 30, 1)
        oled.text("{:02d}/{:02d}/{:04d}".format(day, month, year), 0, 40, 1)
        oled.text("{:02d}:{:02d}:{:02d}".format(hour, minute, second), 0, 50, 1) 
        oled.show()

        utime.sleep(1)






