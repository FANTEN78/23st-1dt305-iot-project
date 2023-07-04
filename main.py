from machine import ADC, I2C, Pin
from libs.pico_i2c_lcd import I2cLcd
from libs.bmp085 import BMP180
import utime
import dht
import machine
import secrets
from libs.mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO


# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(secrets.AIO_CLIENT_ID, secrets.AIO_SERVER, secrets.AIO_PORT, secrets.AIO_USER, secrets.AIO_KEY)
client.connect()
print("Connected to %s" % (secrets.AIO_SERVER))

### Initialize LCD1602 display
lcd1602_i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=400000)
I2C_ADDR = lcd1602_i2c.scan()[0]
lcd = I2cLcd(lcd1602_i2c, I2C_ADDR, 2, 16)
# Empty the LCD display(in case there is something left from previous execution) and then display a start text
lcd.move_to(0,0)
lcd.putstr("                                ")
lcd.putstr("  IoT project  ")
lcd.move_to(0,1)
lcd.putstr("  23ST-1DT305  ")
utime.sleep(2)

### Initialize BMP180 temperature and pressure sensor
bmp180_i2c = I2C(1, sda = Pin(14), scl = Pin(15), freq = 1000000)
bmp = BMP180(bmp180_i2c)
bmp.oversample = 2
bmp.sealevel = 101325
bmp180_temp = "{:.1f}".format(bmp.temperature)
bmp180_press = "{:.2f}".format(bmp.pressure)

### Initialize DHT22 temperature and humidity sensor
DHT22_sensor = dht.DHT22(Pin(13))
DHT22_temp = "{:.1f}".format(DHT22_sensor.temperature())
DHT22_humidity = "{:.1f}".format(DHT22_sensor.humidity())

### Initialize Soil moisture sensor
# Connect Soil moisture sensor data to Rpi Pico GP26
soil_sensor = ADC(Pin(26))
# Soil moisture sensor calibraton values
min_moisture=28000
max_moisture=65535
soil_moisture = (max_moisture-soil_sensor.read_u16())*100 / (max_moisture-min_moisture)
soil_moisture = "{:.1f}".format(soil_moisture)

def publish_data(data, feed):
  print("Publishing: {0} to {1} ... ".format(data, feed), end='')
  try:
      client.publish(topic=feed, msg=str(data))
      print("DONE")
  except Exception as e:
      print("FAILED")

def read_sensor_data():
  print("read_sensor_data() .....")

  # BMP180 sensor measurement
  bmp180_temp = "{:.1f}".format(bmp.temperature)
  publish_data(bmp180_temp, "fanten/feeds/bmp180_temperature")
  bmp180_press = "{:.2f}".format(bmp.pressure)
  publish_data(bmp180_press, "fanten/feeds/bmp180_pressure")
  print("BMP180: Temp: " + str(bmp180_temp) + "C, Pressure: " + str(bmp180_press) + "mbar")
  # Empty the LCD display and then display the new sensor values
  lcd.move_to(0,0)
  lcd.putstr("                                ")
  lcd.putstr("BMP180: " + bmp180_temp + "C")
  lcd.move_to(0,1)
  lcd.putstr(bmp180_press + "mBar")
  utime.sleep(3)

  # DHT22 sensor measurement
  DHT22_sensor.measure()
  DHT22_temp = "{:.1f}".format(DHT22_sensor.temperature())
  publish_data(DHT22_temp, "fanten/feeds/dht22_temperature")
  DHT22_humidity = "{:.1f}".format(DHT22_sensor.humidity())
  publish_data(DHT22_humidity, "fanten/feeds/dht22_humidity")
  print("DHT22: Temp: " + str(DHT22_temp) + "C, Humidity: " + str(DHT22_humidity) + "%")
  # Empty the LCD display and then display the new sensor values
  lcd.move_to(0,0)
  lcd.putstr("                                ")
  lcd.putstr("DHT22: " + DHT22_temp + "C")
  lcd.move_to(0,1)
  lcd.putstr("Humidity: " + DHT22_humidity + "%")
  utime.sleep(3)
  
  # Soil moisture sensor measurement
  soil_moisture = (max_moisture-soil_sensor.read_u16())*100 / (max_moisture-min_moisture) 
  soil_moisture = "{:.1f}".format(soil_moisture)
  publish_data(soil_moisture, "fanten/feeds/soil_moisture")
  print("Soil moisture: " + str(soil_moisture) +"% (adc: "+str(soil_sensor.read_u16())+")")
  # Empty the LCD display and then display the new sensor values
  lcd.move_to(0,0)
  lcd.putstr("                                ")
  lcd.putstr("Soil moisture: ")
  lcd.move_to(0,1)
  lcd.putstr(soil_moisture + "%")
  utime.sleep(3)


try:
  while True:
    read_sensor_data()
    utime.sleep(60)
except:
  print("Error.....")
finally:                  # If an exception is thrown ...
  client.disconnect()     # ... disconnect the client and clean up.
  client = None
  print("Disconnected from Adafruit IO.")
