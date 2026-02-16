from PIL import Image, ImageDraw, ImageFont
import os


size = 32
img = Image.new('RGBA', (size, size), (37, 99, 235, 255))  # primary-600 цвет
draw = ImageDraw.Draw(img)

try:
    
    font = ImageFont.truetype("arial.ttf", 16)
except:
    font = ImageFont.load_default()


text = "П7"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (size - text_width) // 2
y = (size - text_height) // 2 - 2  

draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)


img.save('static/favicon-16.png', sizes=(16, 16))
img.save('static/favicon-32.png', sizes=(32, 32))
img.save('static/favicon-192.png', sizes=(192, 192))
img.save('static/favicon-512.png', sizes=(512, 512))

print("Favicon PNG files created successfully!")
