# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 09:37:34 2018

@author: aerelr
"""

import serial
import csv
import time
import datetime
import struct
import _thread
import util

from mcculw import ul
from mcculw.enums import ULRange, InfoType, BoardInfo,\
    AiChanType, TcType, TempScale
from mcculw.ul import ULError


use_device_detection = True
# Supported PIDs for the USB-2408 and USB-2416 Series
# USB-2408 = 253
# USB-2408-2AO = 254
# USB-2416 = 208
# USB-2416-4AO = 209
supported_pids = [253, 254, 208, 209]

# Set up DAQ channels
channel = 0
board_num = 0
tempscale = 0 #0 == Celsius, 1 == Farenheit, 2 == Kelvin

# Set channel type to TC (thermocouple)
ul.set_config(
    InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE,
    AiChanType.TC)
# Set thermocouple type to type K
ul.set_config(
    InfoType.BOARDINFO, board_num, channel, BoardInfo.CHANTCTYPE,
    TcType.K)
# Set the temperature scale to Fahrenheit
ul.set_config(
    InfoType.BOARDINFO, board_num, channel, BoardInfo.TEMPSCALE,
    TempScale.FAHRENHEIT)
# Set data rate to 60Hz
ul.set_config(
    InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE, 60)


ul_range = ULRange.BIPPT078VOLTS

if use_device_detection:
    ul.ignore_instacal()
    if not util.config_first_detected_device_of_type(
            board_num, supported_pids):
        print("Could not find a supported device.")


def input_thread(a_list):
    input()
    a_list.append(True)
    
fileout = open('dp-sensor.csv', 'a', newline='')
writeCSV = csv.writer(fileout)
    

# Set up serial comms
ser = serial.Serial('COM6', 9600)
print("Communicating via ",ser.name)
send_string = b"\xBF" #This is the string to send to the serial port


def read_stuff(): 
    a_list = []
    _thread.start_new_thread(input_thread, (a_list,))
    
    while not a_list: #Checks for termination keystroke on separate thread

        try: # If no term. keystroke, collect data       
        
            ser.write(send_string) #Sends command send_string to serial port
            
            # Read 2 bytes and converts to integer as little endian,
            # assign to read_serial
            read_serial = struct.unpack('<H',ser.read(size=2)) 
            
            scanvalue = ul.t_in(board_num, channel, tempscale)
           
            csvData = [datetime.datetime.now().timestamp(),read_serial[0], scanvalue]

            print(csvData)
            writeCSV.writerow(csvData)
            time.sleep(1)
            
        except ULError as e:
            # Display the error
            print("A UL error occurred. Code: " + str(e.errorcode)
            + " Message: " + e.message)
            break

print("Press q and Enter to quit.")
read_stuff() 
ser.close()
fileout.close()
