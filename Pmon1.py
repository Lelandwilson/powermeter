import threading
from sys import platform as _platform
import glob
import time
import serial
import socket
import smbus2
import re
from collections import deque
import json
import time
from collections import defaultdict

from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, session


# - local libs and classes - #
from libs.SQLDB import *
from libs.SEARCH4SERAIL import *
from libs.LINUXi2C import *
from libs.USBSERIAL import *
from libs.LOADUSERS import *
from libs.WEBSERVER import *
from libs.DB_SCHED_WRITES import *

from settings_form import SettingsForm1, NetworkForm


SYSTEM = ""
IP = ""
PORT = 8811
SLAVE_ADDRESSES = [2, 3, 4, 5, 6]
I2C_BUS_NO = 1
SERIAL_BAUD = 115200
SECONDS_DATA_DICT = {}
SETTINGS_FILE = 'Settings.txt'
USERLIST = []
USERFILE = "setup/Users.txt"


INTERFACE = ''
ROUTER = ''
DNS = ''
SSID = ''
PASSWORD = ''




# Initialize the sum and count dictionaries
SUMS = defaultdict(lambda: defaultdict(float))
COUNTS = defaultdict(lambda: defaultdict(int))

def setup():
    system = ''
    ip = ''
    # Determnine OS
    if _platform == "linux" or _platform == "linux2":
        system = "linux"
    elif _platform == "darwin":
        system = "mac"
    else:
        system = "?"

    # Determine IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = (s.getsockname()[0])
        s.close()
    except:
        ip = "127.0.0.1"

    return system, ip




if __name__ == "__main__":

    SYSTEM, IP = setup()  # Load setup variables

    mainDB = SQL_liteDB()  # Instantiate Database
    mainDB.initialize_db()  # Startup Database

    # Start scheduling tasks
    schedule_tasks(mainDB,SUMS, COUNTS)  # Begin database task scheduler (time based edits to db)

    if SYSTEM == "linux":
        # Run I2C coms (direct connect), begin as thread
        i2c_connection = linux_I2c()
        try:
            linux_ic2_thread = threading.Thread(target=i2c_connection.i2coms,
                                                args=(I2C_BUS_NO, SLAVE_ADDRESSES, mainDB, SECONDS_DATA_DICT,
                                                      SUMS, COUNTS))
            # linux_ic2_thread.daemon = True
            linux_ic2_thread.start()

        except:
            print("<Error starting Linux I2C direct-connect thread>")

        else:
            pass

    else:
        usbSerial = serach4Serial()
        serialDevice = usbSerial.scan("usbmodem", "usbserial14")
        print("Serial Device found: " + serialDevice)

        if serialDevice != "-1":
            # found usb serial device, begin thread
            connection = readSerialStream()
            try:
                mac_serial_thread = threading.Thread(target=connection.stream,
                                                     args=(serialDevice, SERIAL_BAUD, mainDB, SECONDS_DATA_DICT,
                                                           SUMS, COUNTS))
                # mac_serial_thread.daemon = True
                mac_serial_thread.start()

            except:
                print("<Error starting Linux I2C direct-connect thread>")

            else:
                pass

        else:
            # failed to find usb serial device
            print("Error: could not connect to usb serial device. Check connections")
            time.sleep(5)

    #- Web server stuff -#
    loadUsers(USERFILE, USERLIST)  # PWD for user login
    run_webserver(USERLIST, IP, PORT, SECONDS_DATA_DICT, mainDB)  # start the webserver

# END