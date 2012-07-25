'''
Pololu Minumu9 calculations

import minimu9
imumodule = minimu9.minimu9(0, 0x69, 0x18, 0x1e)


'''

import smbus
import time, math, logging

def delay(ms):
	time.sleep(ms / 1000)


class minimu9():
	'''
	minimu9 connector
	'''
	
	def __init__(self, bus, gyro_addr, accl_addr, magn_addr, DEBUG = 0):
		self.DEBUG = DEBUG
		self.start_logger()		
		
		self.logger.warning('Initializing IMU')
		
		self.logger.info('opening configuration file')
		self.conf_file = open('minimu9.calibrate', "r")
		self.read_config()
				
		self.bus = smbus.SMBus(bus)
		self.logger.info('Open bus ' + str(bus))
		
		self.accelerometer_addr = accl_addr
		self.Accel_Init()
		self.logger.info('Accelerometer started')
		
		self.magnetometer_addr = magn_addr
		self.Compass_Init()
		self.logger.info('Magnetometer started')
		
		self.gyroscoop_addr = gyro_addr
		self.Gyro_Init()
		self.logger.info('Gyroscoop started')
		
		self.logger.warning('Waiting for cold start')
		delay(2000) 
		self.running = 1
		self.logger.info('Minimu9 running')

	def start_logger(self):
		self.logger = logging.getLogger('minimu9')
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		
		hdlr = logging.FileHandler('./log/minimu9.log')
		hdlr.setFormatter(formatter)
		hdlr.setLevel(logging.WARNING)
		
		ch = logging.StreamHandler()
		ch.setFormatter(formatter)
		if self.DEBUG:
			ch.setLevel(logging.DEBUG)
		else:
			ch.setLevel(logging.ERROR)
		
		self.logger.addHandler(hdlr) 
		self.logger.addHandler(ch)

	def Accel_Init(self):
		self.logger.debug('Accelerometer in 8G mode')
		self.bus.write_byte_data(self.accelerometer_addr, 0x20, 0x27) # Put IMU Accl in normal (working mode)
		self.bus.write_byte_data(self.accelerometer_addr, 0x23, 0x30) # Put IMU Accl to 8G bandwidth
		
	def Compass_Init(self):
		self.logger.debug('Magnetometer in normal working mode')
		self.bus.write_byte_data(self.magnetometer_addr, 0x02, 0x00) # Put IMU magn in normal (working mode)
		
	def Gyro_Init(self):
		self.logger.debug('Gyroscope in 2000dps mode')
		self.bus.write_byte_data(self.gyroscoop_addr, 0x20, 0x0F) # Put IMU gyro in normal (working mode)
		self.bus.write_byte_data(self.gyroscoop_addr, 0x23, 0x20) # Put IMU gyro in 2000 dps

	def Read_Gyro(self):
		# read raw gyro
		self.logger.debug('Get Gyroscoop values')
		xl = self.bus.read_byte_data(self.gyroscoop_addr, 0x28)
		xh = self.bus.read_byte_data(self.gyroscoop_addr, 0x29)
		yl = self.bus.read_byte_data(self.gyroscoop_addr, 0x2A)
		yh = self.bus.read_byte_data(self.gyroscoop_addr, 0x2B)
		zl = self.bus.read_byte_data(self.gyroscoop_addr, 0x2C)
		zh = self.bus.read_byte_data(self.gyroscoop_addr, 0x2D)
		
		x = self.combine8to16(xl, xh)
		y = self.combine8to16(yl, yh)
		z = self.combine8to16(zl, zh)		
		return [x, y, z]

	def Read_Accel(self):
		# read raw accel
		self.logger.debug('Get Accelerometer values')
		xl = self.bus.read_byte_data(self.accelerometer_addr, 0x28)
		xh = self.bus.read_byte_data(self.accelerometer_addr, 0x29)
		yl = self.bus.read_byte_data(self.accelerometer_addr, 0x2A)
		yh = self.bus.read_byte_data(self.accelerometer_addr, 0x2B)
		zl = self.bus.read_byte_data(self.accelerometer_addr, 0x2C)
		zh = self.bus.read_byte_data(self.accelerometer_addr, 0x2D)
		
		x = self.combine8to16(xl, xh)
		y = self.combine8to16(yl, yh)
		z = self.combine8to16(zl, zh)
		return [x, y, z]

	def Read_Compass(self):
		# read raw compass data
		self.logger.debug('Get Magnetometer values')
		xh = self.bus.read_byte_data(self.magnetometer_addr, 0x03)
		xl = self.bus.read_byte_data(self.magnetometer_addr, 0x04)
		yh = self.bus.read_byte_data(self.magnetometer_addr, 0x07)
		yl = self.bus.read_byte_data(self.magnetometer_addr, 0x08)
		zh = self.bus.read_byte_data(self.magnetometer_addr, 0x05)
		zl = self.bus.read_byte_data(self.magnetometer_addr, 0x06)
		
		x = self.combine8to16(xl, xh)
		y = self.combine8to16(yl, yh)
		z = self.combine8to16(zl, zh)
		return [x, y, z]
	
	def combine8to16(self, low_byte, high_byte):
		return (((low_byte + (high_byte << 8)) + 2 ** 15) % 2 ** 16 - 2 ** 15)
	
	def calibrate(self):
		'''		
		#TODO
		Open calibration file
		take measurements while rotating imu 
		gather min and max for every value
		store magnetometer min and max
		'''
		self.logger.info("Starting Calibration")
		self.calibration = 1
		calibration_gyro = []
		gyro_max_x = 0
		gyro_max_y = 0
		gyro_max_z = 0
		gyro_min_x = 0
		gyro_min_y = 0
		gyro_min_z = 0
		calibration_accl = []
		accl_max_x = 0
		accl_max_y = 0
		accl_max_z = 0
		accl_min_x = 0
		accl_min_y = 0
		accl_min_z = 0
		calibration_magn = []
		magn_max_x = 0
		magn_max_y = 0
		magn_max_z = 0
		magn_min_x = 0
		magn_min_y = 0
		magn_min_z = 0
		
		for i in range(0, 1000):
			calibration_gyro.append(self.Read_Gyro())
			calibration_accl.append(self.Read_Accel())
			calibration_magn.append(self.Read_Compass())
			time.sleep(0.02)
		
		for gyro_read in calibration_gyro:
			if (gyro_max_x < gyro_read[0]):
				gyro_max_x = gyro_read[0]
			if (gyro_min_x > gyro_read[0]):
				gyro_min_x = gyro_read[0]
			if (gyro_max_y < gyro_read[1]):
				gyro_max_y = gyro_read[1]
			if (gyro_min_y > gyro_read[1]):
				gyro_min_y = gyro_read[1]
			if (gyro_max_z < gyro_read[2]):
				gyro_max_z = gyro_read[2]
			if (gyro_min_z > gyro_read[2]):
				gyro_min_z = gyro_read[2]
		for accl_read in calibration_accl:
			if (accl_max_x < accl_read[0]):
				accl_max_x = accl_read[0]
			if (accl_min_x > accl_read[0]):
				accl_min_x = accl_read[0]
			if (accl_max_y < accl_read[1]):
				accl_max_y = accl_read[1]
			if (accl_min_y > accl_read[1]):
				accl_min_y = accl_read[1]
			if (accl_max_z < accl_read[2]):
				accl_max_z = accl_read[2]
			if (accl_min_z > accl_read[2]):
				accl_min_z = accl_read[2]
		for magn_read in calibration_magn:
			if (magn_max_x < magn_read[0]):
				magn_max_x = magn_read[0]
			if (magn_min_x > magn_read[0]):
				magn_min_x = magn_read[0]
			if (magn_max_y < magn_read[1]):
				magn_max_y = magn_read[1]
			if (magn_min_y > magn_read[1]):
				magn_min_y = magn_read[1]
			if (magn_max_z < magn_read[2]):
				magn_max_z = magn_read[2]
			if (magn_min_z > magn_read[2]):
				magn_min_z = magn_read[2]
		
		
		self.logger.info('Close config file')
		self.conf_file.close()
		self.logger.info('Reopen in write moder: config file')
		self.conf_file = open('minimu9.calibrate', "w")
		
		self.M_X_MIN = magn_min_x
		self.M_X_MAX = magn_max_x
		self.M_Y_MIN = magn_min_y
		self.M_Y_MAX = magn_max_y
		self.M_Z_MIN = magn_min_z
		self.M_Z_MAX = magn_max_z
		
		strw = "XMIN:" + str(magn_min_x) + "\n"
		self.conf_file.write(strw)
		strw = "XMAX:" + str(magn_max_x) + "\n"
		self.conf_file.write(strw)
		strw = "YMIN:" + str(magn_min_y) + "\n"
		self.conf_file.write(strw)
		strw = "YMAX:" + str(magn_max_y) + "\n"
		self.conf_file.write(strw)
		strw = "ZMIN:" + str(magn_min_z) + "\n"
		self.conf_file.write(strw)
		strw = "ZMAX:" + str(magn_max_z) + "\n"
		self.conf_file.write(strw)
		
		self.conf_file.close()
		self.conf_file = open('minimu9.calibrate', "r")
		self.logger.info('Rewrote config file, calibration done')
				 
		
	def read_config(self):
		for line in self.conf_file:
			if (line[:4] == 'XMIN'):
				self.M_X_MIN = int(line[5:])
			elif (line[:4] == 'XMAX'):
				self.M_X_MAX = int(line[5:])
			elif (line[:4] == 'YMIN'):
				self.M_Y_MIN = int(line[5:])
			elif (line[:4] == 'YMAX'):
				self.M_Y_MAX = int(line[5:])
			elif (line[:4] == 'ZMIN'):
				self.M_Z_MIN = int(line[5:])
			elif (line[:4] == 'ZMAX'):
				self.M_Z_MAX = int(line[5:])
