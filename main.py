import time,random
from PIL import Image,ImageDraw,ImageFont

fontTemp = ImageFont.truetype("font/Roboto-Medium.ttf", 136)
textColor = (200,200,200,150)

tempUte = 14
tempInne = 23

while(True):
  im = Image.open("img/bg.png")
  draw = ImageDraw.Draw(im)

  tempUte = 14 + random.randint(0,1)-1
  tempInne = 23 + random.randint(0,1)-1
  
  draw.text((50, 100),str(tempUte)+"°",textColor,font=fontTemp)
  draw.text((560, 290),str(tempInne)+"°",textColor,font=fontTemp)
  im.show()
  time.sleep(2)