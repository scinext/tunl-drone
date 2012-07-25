'''
Created on Jul 15, 2012

@author: Peter Hendriks

Usage:
import navilock551eusb
gps = navilock551eusb.navilock551eusb('/dev/ttyACM2')
gps.start()
'''
from threading import Thread
import serial, time

class navilock551eusb(Thread):
    def __init__(self, port, rate = 115200):
        self.port = serial.Serial(port, rate)
        self.sats_in_view = {}
        Thread.__init__(self)
        
    def run(self):
        self.running = 1
        while self.running:
            line = self.port.readline()
            if (line[:6] == '$GPGSA'):
                self.process_GPGSA(line)
            elif (line[:6] == '$GPGSV'):
                self.process_GPGSV(line)
            elif (line[:6] == '$GPGLL'):
                self.process_GPGLL(line)
            elif (line[:6] == '$GPRMC'):
                self.process_GPRMC(line)
            elif (line[:6] == '$GPVTG'):
                self.process_GPVTG(line)
            elif (line[:6] == '$GPGGA'):
                self.process_GPGGA(line)
            elif (line[:6] == '$GPTXT'):
                self.process_GPTXT(line)
            else:
                print 'Missing: ' + line[:6]
                  
                
                
    def process_GPGSA(self, line):
        [gps_str, checksum] =  line.split('*')
        gpgsa_array = gps_str.split(',')
        self.fix_selection = gpgsa_array[1]
        self.fix = gpgsa_array[2]
        self.pdop = gpgsa_array[15]
        self.hdop = gpgsa_array[16]
        self.vdop = gpgsa_array[17]
        
    def process_GPGSV(self, line):         
        [gps_str, checksum] =  line.split('*')
        gpgsv_array = gps_str.split(',')
        if (gpgsv_array[2] == 1):
            self.sats_in_view = {}
        self.sats_in_view[gpgsv_array[3]] = {'elevation': gpgsv_array[4], 'azimuth': gpgsv_array[5], 'snr': gpgsv_array[6]}
        if (len(gpgsv_array) > 10):
            self.sats_in_view[gpgsv_array[7]] = {'elevation': gpgsv_array[8], 'azimuth': gpgsv_array[9], 'snr': gpgsv_array[10]}
        if (len(gpgsv_array) > 14):
            self.sats_in_view[gpgsv_array[11]] = {'elevation': gpgsv_array[12], 'azimuth': gpgsv_array[13], 'snr': gpgsv_array[14]}
        if (len(gpgsv_array) > 18):
            self.sats_in_view[gpgsv_array[15]] = {'elevation': gpgsv_array[16], 'azimuth': gpgsv_array[17], 'snr': gpgsv_array[18]}
        
        
    def process_GPGLL(self, line):
        [gps_str, checksum] =  line.split('*')
        gpgll_array = gps_str.split(',')
        self.gll_lat = gpgll_array[1]
        self.gll_lat_pole = gpgll_array[2]
        self.gll_lon = gpgll_array[3]
        self.gll_lon_pole = gpgll_array[4]
        self.gll_time = gpgll_array[5]
        self.gll_active = gpgll_array[6]
        
    def process_GPRMC(self, line):
        [gps_str, checksum] =  line.split('*')
        gprmc_array = gps_str.split(',')
        self.time = gprmc_array[1]
        self.status = gprmc_array[2]
        self.lat = gprmc_array[3]
        self.lat_pole = gprmc_array[4]
        self.lon = gprmc_array[5]
        self.lon_pole = gprmc_array[6]
        self.spd = gprmc_array[7]
        self.angle = gprmc_array[8]
        self.date = gprmc_array[9]
        self.magnetic_variation = gprmc_array[10]
        self.magnetic_direction = gprmc_array[11]
        print self.lon + ' ' + self.lon_pole + '   -   ' + self.lat + ' ' + self.lat_pole
        
    def process_GPVTG(self, line):
        [gps_str, checksum] =  line.split('*')
        gpvtg_array = gps_str.split(',')
        self.true_track = gpvtg_array[1]
        self.true_magnetic_track = gpvtg_array[3]
        self.true_ground_speed_knots = gpvtg_array[5]
        self.true_ground_speed_kilometers = gpvtg_array[7]
        print self.true_ground_speed_kilometers
        
    def process_GPGGA(self, line):
        [gps_str, checksum] =  line.split('*')
        gpgga_array = gps_str.split(',')
        self.time = gpgga_array[1]
        self.lat = gpgga_array[2]
        self.lat_pole = gpgga_array[3]
        self.lon = gpgga_array[4]
        self.lon_pole = gpgga_array[5]
        self.status = gpgga_array[6]
        self.hdop = gpgga_array[7]
        self.altitude_meters = gpgga_array[8]
        self.geoid_height = gpgga_array[10]

    def process_GPTXT(self, line):
        [gps_str, checksum] =  line.split('*')
        gptxt_array = gps_str.split(',')
        
    def output_array(self):
        location_array = (self.lat, self.lat_pole, self.lon, self.lon_pole, self.spd, self.altitude_meters)
        gps_array = (self.fix, self.pdop, self.hdop, self.vdop)
        output_array = {'location' : location_array, 'gps' : gps_array}
        return output_array