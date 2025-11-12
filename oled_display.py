#!/usr/bin/env python3

import os
import glob
import time
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import Image, ImageFont

# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        # temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

# NB ssd1306 devices are monochromatic; a pixel is enabled with
#    white and disabled with black.
# NB the ssd1306 class has no way of knowing the device resolution/size.
device = ssd1306(i2c(port=1, address=0x3c), width=128, height=64, rotate=0)

# set the contrast to minimum.
device.contrast(1)

fontTitle = ImageFont.truetype("fonts/Monaco.ttf", 24)
fontMessage = ImageFont.truetype("fonts/Monaco.ttf", 14)

# File path for message
title_file = "/opt/bin/title.txt"  # Replace with your file path
message_file = "/opt/bin/message.txt"  # Replace with your file path

# Function to read message from file
def read_message(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()  # Read the file content and remove trailing spaces/newlines
    except FileNotFoundError:
        return "File not found"  # Return a default message if the file doesn't exist
    except Exception as e:
        return str(e)

while True:
    with canvas(device, dither=True) as draw:
        celsius = read_temp()
        # draw.rectangle(device.bounding_box, outline='white', fill='black')
        title = read_message(title_file)
        message = read_message(message_file)

        # Get bounding box for text
        x0, y0, x1, y1 = draw.textbbox((0, 0), text=title, font=fontTitle)
        text_width_title = x1 - x0
        text_height_title = y1 - y0

        # (text_width_title + ((device.width - text_width_title) // 2), 0),
        # Center the text
        draw.text(
            (0, 0),
            title,
            font=fontTitle,
            fill="white"
        )

        # Get bounding box for text
        x2, y2, x3, y3 = draw.textbbox((0, 0), text=message, font=fontMessage)
        # text_width_message = x3 - x2
        text_height_message = y3 - y2
        draw.text(
            (0, text_height_title + 10),
            message,
            font=fontMessage,
            fill="white"
        )

    time.sleep(1)
