#!/usr/bin/env python3
import sys,time,os,Adafruit_DHT,logging,signal,threading
import RPi.GPIO as GPIO
from Adafruit_IO import Client, Feed
from w1thermsensor import W1ThermSensor, Unit
from PIL import Image,ImageDraw,ImageFont

# Send power to sensors
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setup(20, GPIO.OUT, initial=1)
GPIO.setup(26, GPIO.OUT, initial=1)
time.sleep(2)

# Config
logging.basicConfig(level=logging.INFO)

fontTemp = ImageFont.truetype("font/Roboto-Medium.ttf", 136)
textColor = (255,255,255,255)

UPDATE_TIME = 60
DHT_PIN = 19
DHT_SENSOR = Adafruit_DHT.DHT22
DS_SENSOR = None

while DS_SENSOR is None:
  try:
    DS_SENSOR = W1ThermSensor()
  except:
    logging.error("Error connecting to DS sensor")
  time.sleep(1)

logging.debug('Config ok')

ADAFRUIT_IO_USERNAME = "olehenfo"
ADAFRUIT_IO_KEY = "aio_DsaK3203FbMjD7nGmcEbjYS6QNhy"

# Adafruit IO
def connectAdaIO():
  try:
    logging.info('Connecting to AIO...')
    aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
    inside_feed = aio.feeds('hytte-temp-inside')
    humid_feed = aio.feeds('hytte-humid-inside')
    outside_feed = aio.feeds('hytte-temp-outside')
    logging.debug('IO connected')
    return {"aio":aio,"itempfeed":inside_feed,"otempfeed":outside_feed,"humidfeed":humid_feed}
  except:
    logging.error('Error connecting to IO')
    return None

adaIO = None
while adaIO is None:
  adaIO = connectAdaIO()
  time.sleep(5)

def getTemp():
  try:
    # Get sensor readings
    humidInne, tempInne = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    tempUte = DS_SENSOR.get_temperature()

    logging.info('TempInne={0:0.1f}*C TempUte={1:0.1f} humidInne={2:0.1f}%'.format(tempInne, tempUte, humidInne))

    # Send to IO
    aio = adaIO["aio"]
    aio.send(adaIO["itempfeed"].key, str('%.2f'%(tempInne)))
    aio.send(adaIO["humidfeed"].key, str('%.2f'%(humidInne)))
    aio.send(adaIO["otempfeed"].key, str('%.2f'%(tempUte)))
  except:
    logging.error("Error getting temperature")
    return False

  # Draw image on screen
  drawImage('%.1f'%(tempInne),'%.1f'%(humidInne),'%.1f'%(tempUte))
  return True

def drawImage(inside,humid,outside):
  try:
    time.sleep(1)
    im = Image.open("img/bg.png")
    draw = ImageDraw.Draw(im)
    draw.text((50, 50),str(inside)+"°",textColor,font=fontTemp)
    draw.text((50, 200),str(humid)+"%",textColor,font=fontTemp)
    draw.text((50, 600),str(outside)+"°",textColor,font=fontTemp)
    im.save("img/image.png")
    os.system("sudo pkill fbi")
    os.system("sudo fbi --autozoom --noverbose --vt 1 img/image.png")
    return True
  except:
    logging.error("Error drawing image")
    return False

def main():
  getTemp()
  time.sleep(1)
  threading.Timer(UPDATE_TIME,main).start()

# Start main loop
main()

def signal_handler(sig, frame):
  logging.info('Exiting...')
  GPIO.cleanup()
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.pause()
