#!/usr/bin/env python3

import os
import glob
import time
from datetime import datetime
from typing import AnyStr, Tuple

import w1thermsensor

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import Image, ImageFont
from w1thermsensor import W1ThermSensor

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device2_folder = glob.glob(base_dir + '28*')[1]
device_resolution_file = device_folder + '/resolution'
device_file = device_folder + '/w1_slave'
device2_file = device2_folder + '/w1_slave'

sensor = W1ThermSensor()  # Initialize the sensor

def read_w1_temp():
    """
    Reads the temperature from a 1-Wire temperature sensor using w1thermsensor library.

    Returns:
        float: The temperature in Celsius.
    """
    try:
#        sensor = W1ThermSensor()  # Initialize the sensor
        temp_c = sensor.get_temperature()  # Get temperature in Celsius
        return temp_c
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return None

def read_all_w1_temp():
    """
    Reads the temperature from a 1-Wire temperature sensor using w1thermsensor library.

    Returns:
        float: The temperature in Celsius.
    """
    try:
        temps = []
#        for sensor in W1ThermSensor.get_available_sensors():
#           temps.append(sensor.get_temperature())  # Get temperature in Celsius
        sensors = {sensor.id: sensor.get_temperature() for sensor in W1ThermSensor.get_available_sensors()}
#  Sensor 1 (00000037e1d9) measured temperature: 20.0 celsius
#  Sensor 2 (00000035029c) measured temperature: 3.25 celsius
#        order = ["00000035029c", "00000037e1d9"]
        order = ["00000037e1d9", "00000035029c"]
        temps = [sensors[sid] for sid in order if sid in sensors]

#        print(temps)

        return temps
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return None


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read2_temp_raw():
    f = open(device2_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def write_resolution(r):
    f = open(device_resolution_file, 'w')
    f.write(r)
    f.close()
    return


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

def read2_temp():
    lines = read2_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read2_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f


def write_message(file_path, text):
    """
    Writes the given message to a file at the specified file path.

    Args:
        file_path (str): The path of the file to write to.
        text (str): The message to write into the file.

    Returns:
        bool: True if the operation succeeds, False otherwise.
    """
    try:
        with open(file_path, 'w') as f:
            f.write(text.strip())
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False


def get_ip_address_os():
    """
    Gets the IP address using the `hostname` command.

    Returns:
        str: The IP address or an error message.
    """
    try:
        ip_address = os.popen("hostname -I").read().strip()
        return ip_address
    except Exception as e:
        return f"Error retrieving IP address: {e}"


def get_net_conn_count_os():
    """
    Gets the IP address using the `hostname` command.

    Returns:
        str: The IP address or an error message.
    """
    try:
        count = os.popen("sudo -s netstat -naltp | grep ESTABLISHED | wc -l").read().strip()
        return count
    except Exception as e:
        return f"Error retrieving IP address: {e}"


def get_free_space():
    """
    Gets the IP address using the `hostname` command.

    Returns:
        str: The IP address or an error message.
    """
    try:
        count = os.popen("df -h | grep -v Filesystem | grep -v tmpfs | awk '{ print $2\"/\"$4 }'").read().strip()
        return count
    except Exception as e:
        return f"Error retrieving IP address: {e}"


def get_date():
    """
    Returns the current date in YYYY-MM-DD format.

    Returns:
        str: The current date as a string.
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_time():
    """
    Returns the current time in HH:MM:SS format.

    Returns:
        str: The current time as a string.
    """
    return datetime.now().strftime("%H:%M:%S")


def rpi_temp():
    """
    Reads the CPU temperature of the Raspberry Pi.

    Returns:
        float: The CPU temperature in Celsius, or None if unable to read.
    """
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
            temp_raw = file.read().strip()
            temp_c = float(temp_raw) / 1000.0  # Convert from millidegree Celsius to Celsius
            return temp_c
    except FileNotFoundError:
        print("Temperature file not found. Are you running on a Raspberry Pi?")
        return None
    except Exception as e:
        print(f"Error reading CPU temperature: {e}")
        return None


# File path for message
# title_file = "/opt/bin/title.txt"  # Replace with your file path
# message_file = "/opt/bin/message.txt"  # Replace with your file path

# NB ssd1306 devices are monochromatic; a pixel is enabled with
#    white and disabled with black.
# NB the ssd1306 class has no way of knowing the device resolution/size.
device = ssd1306(i2c(port=1, address=0x3c), width=128, height=64, rotate=0)

# set the contrast to minimum.
device.contrast(1)

fontTitle = ImageFont.truetype("fonts/Monaco.ttf", 24)
fontMessage = ImageFont.truetype("fonts/Monaco.ttf", 24)


# File path for message
# title_file = "/opt/bin/title.txt"  # Replace with your file path
# message_file = "/opt/bin/message.txt"  # Replace with your file path

# Function to read message from file
def read_message(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()  # Read the file content and remove trailing spaces/newlines
    except FileNotFoundError:
        return "File not found"  # Return a default message if the file doesn't exist
    except Exception as e:
        return str(e)


def show_info(title: str, message: str, progress: Tuple[int, int]):
    with canvas(device, dither=True) as draw:
        # draw.rectangle(device.bounding_box, outline='white', fill='black')
        # title = read_message(title_file)
        # message = read_message(message_file)

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

        total = (device.height // progress[1] - 1)
        for p in range(progress[0] + 1):
            x = device.width - 1  # X-coordinate of the circle's center
            # y = (device.height // total) * p
            y = device.height - ((p - 1) * total)
            draw.rectangle((x, y - total, x, y), outline='white', fill='black')


each: int = 8
while True:
    t = each
    z = 0
    while t > -1:
        values = read_all_w1_temp()
        #r = list(reversed(values))
        #v = r.pop()
        v = values.pop()
        #title = " ".join(f"{v:.1f}" for v in values) + " ºC"
        title = f"{v:.1f} ºC"
        #" ".join(f"{v:.1f}" for v in values) + " ºC"
        #value = read_w1_temp()
        #title = f"{value:.1f} ºC"
        if z == 0:
            #title = " ".join(f"{v:.1f}" for v in values) + " ºC"
            #message = " ".join(f"{v:.1f}" for v in r) + " ºC" + f"{get_date()}\nRPI: {rpi_temp():.2f} ºC"
            #message = " ".join(f"{v:.1f}" for v in values) + " ºC\n" + f"{get_date()}\n"
            message = " ".join(f"{v:.1f}" for v in values) + " ºC"
            z = 1
        else:
            message = " ".join(f"{v:.1f}" for v in values) + " ºC"
            #message = " ".join(f"{v:.1f}" for v in values) + " ºC\n" + f"{get_date()}\n"
            #message = " ".join(f"{v:.1f}" for v in r) + " ºC" + f"{get_date()}\nRPI: {rpi_temp():.2f} ºC"
            #message = f"{get_time()}\nRPI: {rpi_temp():.2f} ºC"
            z = 0
        show_info(title, message, (t, each))
        time.sleep(0.5)
        t = t - 1

    # t = each
    # while t > -1:
    #    show_info(title, message, (t, each))
    #    time.sleep(0.2)
    #    t = t - 1

    # t = each
    # while t > -1:
    #     title = f"∴ {get_net_conn_count_os()}"
    #     message = get_ip_address_os().replace(" ", "\n")
    #     show_info(title, message, (t, each))
    #     time.sleep(0.5)
    #     t = t - 1

    # t = each
    # while t > -1:
    #     title = f"space: "
    #     message = get_free_space()
    #     show_info(title, message, (t, each))
    #     time.sleep(0.5)
    #     t = t - 1
