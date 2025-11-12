#!/usr/bin/env python3

import glob
import os
import time
from datetime import datetime

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
title_file = "/opt/bin/title.txt"  # Replace with your file path
message_file = "/opt/bin/message.txt"  # Replace with your file path

while True:
    value = read_temp()

    title = f"{value[0]:.2f} Cº"
    write_message(title_file, title)

    message = ""
    write_message(message_file, message)

    time.sleep(3)

    title = get_time()
    write_message(title_file, title)

    message = get_date()
    write_message(message_file, message)

    time.sleep(5)

    title = f"{rpi_temp():.2f} Cº"
    write_message(title_file, title)

    message = get_ip_address_os().replace(" ", "\n")
    write_message(message_file, message)

    time.sleep(5)

