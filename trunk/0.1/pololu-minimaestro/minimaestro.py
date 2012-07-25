'''
Created on Jul 15, 2012

@author: Peter Hendriks

Usage:
import minimaestro
mm = minimaestro.minimaestro('/dev/ttyACM0')
'''
import serial, time, binascii

class minimaestro():
    '''
    The mini maestro needs to be configured before usage. 
    There is no check on input or output for channels.
    Because multiple perhipials will use this class to gather data and set servo's a wait is incorperated. 
    While another process is using the mini maestro other processes should wait. (Need to check this in real life)
    '''
    def __init__(self, port, rate = 115200):
        self.running_query = 1
        self.port = serial.Serial(port, rate)
        self.running_query = 0

    def set_port(self, port_number, position):
        while self.running_query:
            time.sleep(0.0001)
        self.running_query = 1        
        position_array = self.position_encode(position)
        msg = chr(0x84) + chr(port_number) + chr(position_array[1]) + chr(position_array[0])
        self.port.write(msg)
        self.running_query = 0        
        
    def set_multiple(self, start_port, position_array):
        while self.running_query:
            time.sleep(0.0001)
        self.running_query = 1        
        position_string = ""
        number = 0
        for position in position_array:
            number = number + 1
            position_bits = self.position_encode(position)
            position_string += chr(position_bits[0]) + chr(position_bits[1])             
        msg = chr(0x9F) + chr(number) + position_string
        self.port.write(msg)                
        self.running_query = 0        

    def get_port(self, port_number):
        while self.running_query:
            time.sleep(0.0001)
        self.running_query = 1        
        msg = chr(0x90) + chr(port_number)
        self.port.write(msg)
        time.sleep(0.001)
        response1 = self.port.read(1)
        response2 = self.port.read(1)
        lb = int(binascii.hexlify(response1), 16)
        hb = int(binascii.hexlify(response2), 16)
        position = self.position_decode(lb, hb)
        self.running_query = 0
        return position
            
    def position_encode(self, position):
        lb = position & 0x7F
        hb = (position >> 7) & 0x7F
        return (lb, hb)
        
    def position_decode(self, lb, hb):
        binlb = bin(int(lb))[2:]
        binhb = bin(int(hb))[2:]
        return int(binhb + binlb, 2)

    def get_voltage(self, port_number):
        position = self.get_port(port_number)
        bitpervolt = 5.0 / 1023
        return position * bitpervolt
