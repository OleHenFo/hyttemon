import time,os,Adafruit_DHT,logging
from Adafruit_IO import Client, Feed
from w1thermsensor import W1ThermSensor, Unit
from PIL import Image,ImageDraw,ImageFont

# Config
logging.basicConfig(level=logging.DEBUG)

UPDATE_TIME = 5
DHT_PIN = 20
DS_SENSOR = W1ThermSensor()
DHT_SENSOR = Adafruit_DHT.DHT22
logging.debug('Config ok')

# Adafruit IO
ADAFRUIT_IO_KEY = 'aio_PLQR23xiEZARFzxsRgFkKLo1joGu'
ADAFRUIT_IO_USERNAME = 'olehenfo'
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
inside_temperature_feed = aio.feeds('hytte_temp_inside')
inside_humidity_feed = aio.feeds('hytte_humid_inside')
outside_temperature_feed = aio.feeds('hytte_temp_outside')
logging.debug('IO connected')

while(True):
  # Get sensor readings
  humidInne, tempInne = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
  tempUte = 0

  logging.debug('TempInne={0:0.1f}*C TempUte={1:0.1f} humidInne={2:0.1f}%'.format(tempInne, tempUte, humidInne))

  # Send to IO
  aio.send(inside_temperature_feed.key, str('%.2f'%(tempInne)))
  aio.send(inside_humidity_feed.key, str('%.2f'%(humidInne)))
  aio.send(outside_temperature_feed.key, str('%.2f'%(tempUte)))

  # Draw image on screen
  drawImage(tempInne,humidInne,)

  # Wait before update
  time.sleep(UPDATE_TIME)

  

def drawImage(inside,humid,outside=0):
  fontTemp = ImageFont.truetype("font/Roboto-Medium.ttf", 136)
  textColor = (200,200,200,150)
  im = Image.open("img/bg.png")
  draw = ImageDraw.Draw(im)
  draw.text((50, 100),str(inside)+"°",textColor,font=fontTemp)
  draw.text((50, 400),str(humid)+"°",textColor,font=fontTemp)
  im.save("img/image.png")
  os.system("sudo fbi --autozoom --noverbose --vt 1 img/image.png")
