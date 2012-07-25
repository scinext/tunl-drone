'''
Container for IMU AHRS calculations

Usage:
------------------------------------
import imumodule (depending on IMU)
import imu

imumodule = imumodule.class(vars)
imu = imu.imu(imumodule)
imu.start()
------------------------------------

information can be gathered from various variables:
imu.MAG_Heading
imu.roll
imu.pitch
imu.yaw




import minimu9
imumodule = minimu9.minimu9(0, 0x69, 0x18, 0x1e)
import imu
imu = imu.imu(imumodule)
imu.start()

'''

from threading import Thread
from vector import *
from matrix import *
import time, math, logging

def delay(ms):
	time.sleep(ms / 1000)

class imu(Thread):
	'''
	Thread for reading from imu-module and doing all the calculations
	'''
	Gyro_Gain_X = 0.07 ##X axis Gyro gain
	Gyro_Gain_Y = 0.07 ##Y axis Gyro gain
	Gyro_Gain_Z = 0.07 ##Z axis Gyro gain
	
	Kp_ROLLPITCH = 0.02
	Ki_ROLLPITCH = 0.00002
	Kp_YAW = 1.2
	Ki_YAW = 0.00002

	###########################################################
	## Uncomment the below line to use this axis definition: ##
	## X axis pointing forward
	## Y axis pointing to the right
	## and Z axis pointing down.
	## Positive pitch : nose up
	## Positive roll : right wing down
	## Positive yaw : clockwise
	SENSOR_SIGN = [ 1, 1, 1, -1, -1, -1, 1, 1, 1 ] ## Correct directions x,y,z - gyro, accelerometer, magnetometer
	###########################################################	
	## Uncomment the below line to use this axis definition: ##
	## X axis pointing forward
	## Y axis pointing to the left
	## and Z axis pointing up.
	## Positive pitch : nose down
	## Positive roll : right wing down
	## Positive yaw : counterclockwise
	#SENSOR_SIGN = [1,-1,-1,-1,1,1,1,-1,-1] ##Correct directions x,y,z - gyro, accelerometer, magnetometer
	
	'''
	LSM303 accelerometer: 8 g sensitivity
	3.8 mg/digit; 1 g = 256
	'''
	GRAVITY = 256
	'''
	*For debugging purposes*
	OUTPUTMODE = 1 will print the corrected data,
	OUTPUTMODE = 0 will print uncorrected data of the gyros (with drift)
	'''
	OUTPUTMODE = 1
	
	G_Dt = 0.02 				## Integration time (DCM algorithm)  We will run the integration loop at 50Hz if possible

	timer = 0 				## general purpuse timer
	timer_old = 0
	timer24 = 0 				## Second timer used to print values
	AN = [ 0, 0, 0, 0, 0, 0 ] 				##array that stores the gyro and accelerometer data
	AN_OFFSET = [ 0, 0, 0, 0, 0, 0 ] 	## Array that stores the Offset of the sensors

	gyro_x = 0
	gyro_y = 0
	gyro_z = 0
	accel_x = 0
	accel_y = 0
	accel_z = 0
	magnetom_x = 0
	magnetom_y = 0
	magnetom_z = 0
	c_magnetom_x = 0.0
	c_magnetom_y = 0.0
	c_magnetom_z = 0.0
	MAG_Heading = 0.0

	Accel_Vector = [ 0.0, 0.0, 0.0 ] # Store the acceleration in a vector
	Gyro_Vector = [ 0.0, 0.0, 0.0 ] ##Store the gyros turn rate in a vector
	Omega_Vector = [ 0.0, 0.0, 0.0 ]  ##Corrected Gyro_Vector data
	Omega_P = [ 0.0, 0.0, 0.0 ] ##Omega Proportional correction
	Omega_I = [ 0.0, 0.0, 0.0 ] ##Omega Integrator
	Omega = [ 0.0, 0.0, 0.0 ] 

	## Euler angles
	roll = 0.0 
	pitch = 0.0
	yaw = 0.0

	errorRollPitch = [ 0.0, 0.0, 0.0 ] 
	errorYaw = [ 0.0, 0.0, 0.0 ] 

	counter = 0 
	gyro_sat = 0 

	DCM_Matrix = [ [ 1.0, 0.0, 0.0 ], [ 0.0, 1.0, 0.0 ], [ 0.0, 0.0, 1.0 ] ] 
	Update_Matrix = [ [ 0.0, 1.0, 2.0 ], [ 3.0, 4.0, 5.0 ], [ 6.0, 7.0, 8.0 ] ]  ##Gyros here


	Temporary_Matrix = [ [ 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0 ] ] 

	def __init__(self, imumodule, DEBUG = 0):
		self.imumodule = imumodule
		self.DEBUG = DEBUG
		self.start_logger()
		Thread.__init__(self)

	def run(self):
		self.running = 1
		for i in range(0, 32): ## We take some readings...
			self.logger.warning("Taking reading #" + str(i))
			self.Read_Gyro() 
			self.Read_Accel() 
			for y in range(0, 6): ## Cumulate values
				self.AN_OFFSET[y] += self.AN[y] 
			delay(20) 

		self.logger.warning("Offset readings complete")
				
		for y in range(0, 6):
			self.AN_OFFSET[y] = self.AN_OFFSET[y] / 32 

		self.AN_OFFSET[5] -= self.GRAVITY * self.SENSOR_SIGN[5] 

		self.logger.warning("Offset:")
		for y in range(0, 6):
			self.logger.warning(str(self.AN_OFFSET[y])) 

		delay(20) 
		self.counter = 0 
		self.timer = 0
		while self.running:
			# TODO run
			self.run_loop()
	
	def run_loop(self):
		self.counter = self.counter + 1
		self.timer_old = self.timer 
		self.timer = int(time.time() * 1000)
		if (self.timer > self.timer_old):
			G_Dt = (self.timer - self.timer_old) / 1000.0   ## Real time of loop run. We use this on the DCM algorithm (gyro integration time)
		else:
			G_Dt = 0.0

		## *** DCM algorithm
		## Data adquisition
		self.Read_Gyro()   ## This read gyro data
		self.Read_Accel()   ## Read I2C accelerometer

		if (self.counter > 5):  ## Read compass data at 10Hz... (5 loop runs)
			self.counter = 0 
			self.Read_Compass()   ## Read I2C magnetometer
			self.Compass_Heading()   ## Calculate magnetic heading
		
		## Calculations...
		self.Matrix_update() 
		self.Normalize() 
		self.Drift_correction() 
		self.Euler_angles()

	def start_logger(self):
		self.logger = logging.getLogger('imu')
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		
		hdlr = logging.FileHandler('./log/imu.log')
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
	
	def Read_Gyro(self):
		values = self.imumodule.Read_Gyro()   ## This read gyro data

		self.AN[0] = values[0]
		self.AN[1] = values[1]
		self.AN[2] = values[2]
		self.gyro_x = self.SENSOR_SIGN[0] * (self.AN[0] - self.AN_OFFSET[0]) 
		self.gyro_y = self.SENSOR_SIGN[1] * (self.AN[1] - self.AN_OFFSET[1]) 
		self.gyro_z = self.SENSOR_SIGN[2] * (self.AN[2] - self.AN_OFFSET[2]) 
				
	def Read_Accel(self):
		values = self.imumodule.Read_Accel()   ## Read I2C accelerometer
		
		self.AN[3] = values[0]
		self.AN[4] = values[1]
		self.AN[5] = values[2]
		self.accel_x = self.SENSOR_SIGN[3] * (self.AN[3] - self.AN_OFFSET[3]) 
		self.accel_y = self.SENSOR_SIGN[4] * (self.AN[4] - self.AN_OFFSET[4]) 
		self.accel_z = self.SENSOR_SIGN[5] * (self.AN[5] - self.AN_OFFSET[5]) 

	def Read_Compass(self):
		values = self.imumodule.Read_Compass()   ## Read I2C magnetometer

		self.magnetom_x = self.SENSOR_SIGN[6] * values[0]
		self.magnetom_y = self.SENSOR_SIGN[7] * values[1]
		self.magnetom_z = self.SENSOR_SIGN[8] * values[2]

	def Matrix_update(self):
			self.Gyro_Vector[0] = self.Gyro_Scaled_X(self.gyro_x)  ##gyro x roll
			self.Gyro_Vector[1] = self.Gyro_Scaled_Y(self.gyro_y)  ##gyro y pitch
			self.Gyro_Vector[2] = self.Gyro_Scaled_Z(self.gyro_z)  ##gyro Z yaw
		
			self.Accel_Vector[0] = self.accel_x 
			self.Accel_Vector[1] = self.accel_y 
			self.Accel_Vector[2] = self.accel_z 
		
			self.Omega = Vector_Add(self.Gyro_Vector, self.Omega_I)  ##adding proportional term
			self.Omega_Vector = Vector_Add(self.Omega, self.Omega_P)  ##adding Integrator term
		
			##Accel_adjust()     ##Remove centrifugal acceleration.   We are not using this function in this version - we have no speed measurement
		
			if (self.OUTPUTMODE == 1):
				self.Update_Matrix[0][0] = 0.0 
				self.Update_Matrix[0][1] = -self.G_Dt * self.Omega_Vector[2] ##-z
				self.Update_Matrix[0][2] = self.G_Dt * self.Omega_Vector[1] ##y
				self.Update_Matrix[1][0] = self.G_Dt * self.Omega_Vector[2] ##z
				self.Update_Matrix[1][1] = 0.0 
				self.Update_Matrix[1][2] = -self.G_Dt * self.Omega_Vector[0] ##-x
				self.Update_Matrix[2][0] = -self.G_Dt * self.Omega_Vector[1] ##-y
				self.Update_Matrix[2][1] = self.G_Dt * self.Omega_Vector[0] ##x
				self.Update_Matrix[2][2] = 0.0 
			else:                    ## Uncorrected data (no drift correction)
				self.Update_Matrix[0][0] = 0.0 
				self.Update_Matrix[0][1] = -self.G_Dt * self.Gyro_Vector[2] ##-z
				self.Update_Matrix[0][2] = self.G_Dt * self.Gyro_Vector[1] ##y
				self.Update_Matrix[1][0] = self.G_Dt * self.Gyro_Vector[2] ##z
				self.Update_Matrix[1][1] = 0.0 
				self.Update_Matrix[1][2] = -self.G_Dt * self.Gyro_Vector[0] 
				self.Update_Matrix[2][0] = -self.G_Dt * self.Gyro_Vector[1] 
				self.Update_Matrix[2][1] = self.G_Dt * self.Gyro_Vector[0] 
				self.Update_Matrix[2][2] = 0.0 
		
			self.Temporary_Matrix = Matrix_Multiply(self.DCM_Matrix, self.Update_Matrix)  ##a*b=c
			
			for x in range(0, 3):
				for y in range(0, 3):
					self.DCM_Matrix[x][y] += self.Temporary_Matrix[x][y]

	def Normalize(self):
		error = 0.0
		temporary = [ [ 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0 ] ]
		renorm = 0.0
	
		error = -Vector_Dot_Product(self.DCM_Matrix[0], self.DCM_Matrix[1]) * .5 ##eq.19
	
		temporary[0] = Vector_Scale(self.DCM_Matrix[1], error) ##eq.19
		temporary[1] = Vector_Scale(self.DCM_Matrix[0], error) ##eq.19
	
		temporary[0] = Vector_Add(temporary[0], self.DCM_Matrix[0])##eq.19
		temporary[1] = Vector_Add(temporary[1], self.DCM_Matrix[1])##eq.19
	
		temporary[2] = Vector_Cross_Product(temporary[0], temporary[1]) ## c= a x b ##eq.20
	
		renorm = .5 * (3 - Vector_Dot_Product(temporary[0], temporary[0])) ##eq.21
		self.DCM_Matrix[0] = Vector_Scale(temporary[0], renorm)
	
		renorm = .5 * (3 - Vector_Dot_Product(temporary[1], temporary[1])) ##eq.21
		self.DCM_Matrix[1] = Vector_Scale(temporary[1], renorm)
	
		renorm = .5 * (3 - Vector_Dot_Product(temporary[2], temporary[2])) ##eq.21
		self.DCM_Matrix[2] = Vector_Scale(temporary[2], renorm)
		
	def Drift_correction(self):
		mag_heading_x = 0.0
		mag_heading_y = 0.0
		errorCourse = 0.0
		
		##Compensation the Roll, Pitch and Yaw drift.
		Scaled_Omega_P = [ 0.0, 0.0, 0.0 ]  
		Scaled_Omega_I = [ 0.0, 0.0, 0.0 ]  
		Accel_magnitude = 0.0 
		Accel_weight = 0.0 
	
		##*****Roll and Pitch***************
	
		## Calculate the magnitude of the accelerometer vector
		Accel_magnitude = math.sqrt(self.Accel_Vector[0] * self.Accel_Vector[0] + self.Accel_Vector[1] * self.Accel_Vector[1] + self.Accel_Vector[2] * self.Accel_Vector[2]) 
		Accel_magnitude = Accel_magnitude / self.GRAVITY  ## Scale to gravity.
		## Dynamic weighting of accelerometer info (reliability filter)
		## Weight for accelerometer info (<0.5G = 0.0, 1G = 1.0 , >1.5G = 0.0)
		Accel_weight = self.constrain(1 - 2 * abs(1 - Accel_magnitude), 0, 1)  ##
	
		self.errorRollPitch = Vector_Cross_Product(self.Accel_Vector, self.DCM_Matrix[2])  ##adjust the ground of reference
		self.Omega_P = Vector_Scale(self.errorRollPitch, (self.Kp_ROLLPITCH * Accel_weight)) 
	
		Scaled_Omega_I = Vector_Scale(self.errorRollPitch, (self.Ki_ROLLPITCH * Accel_weight)) 
		self.Omega_I = Vector_Add(self.Omega_I, Scaled_Omega_I) 
	
		##*****YAW***************
		## We make the gyro YAW drift correction based on compass magnetic heading
	
		mag_heading_x = math.cos(self.MAG_Heading) 
		mag_heading_y = math.sin(self.MAG_Heading) 
		errorCourse = (self.DCM_Matrix[0][0] * mag_heading_y) - (self.DCM_Matrix[1][0] * mag_heading_x)  ##Calculating YAW error
		self.errorYaw = Vector_Scale(self.DCM_Matrix[2], errorCourse)  ##Applys the yaw correction to the XYZ rotation of the aircraft, depeding the position.
	
		Scaled_Omega_P = Vector_Scale(self.errorYaw, self.Kp_YAW) ##.01proportional of YAW.
		self.Omega_P = Vector_Add(self.Omega_P, Scaled_Omega_P) ##Adding  Proportional.
	
		Scaled_Omega_I = Vector_Scale(self.errorYaw, self.Ki_YAW) ##.00001Integrator
		self.Omega_I = Vector_Add(self.Omega_I, Scaled_Omega_I) ##adding integrator to the Omega_I

	def Euler_angles(self):
		self.pitch = -math.asin(self.DCM_Matrix[2][0])
		self.roll = math.atan2(self.DCM_Matrix[2][1], self.DCM_Matrix[2][2])
		self.yaw = math.atan2(self.DCM_Matrix[1][0], self.DCM_Matrix[0][0])

	def Compass_Heading(self):
		MAG_X = 0.0
		MAG_Y = 0.0
		cos_roll = 0.0
		sin_roll = 0.0
		cos_pitch = 0.0
		sin_pitch = 0.0
	
		cos_roll = math.cos(self.roll) 
		sin_roll = math.sin(self.roll) 
		cos_pitch = math.cos(self.pitch) 
		sin_pitch = math.sin(self.pitch) 
	
		## adjust for LSM303 compass axis offsets/sensitivity differences by scaling to +/-0.5 range
		self.c_magnetom_x = (float) (self.magnetom_x - self.SENSOR_SIGN[6] * self.imumodule.M_X_MIN) / (self.imumodule.M_X_MAX - self.imumodule.M_X_MIN) - self.SENSOR_SIGN[6] * 0.5 
		self.c_magnetom_y = (float) (self.magnetom_y - self.SENSOR_SIGN[7] * self.imumodule.M_Y_MIN) / (self.imumodule.M_Y_MAX - self.imumodule.M_Y_MIN) - self.SENSOR_SIGN[7] * 0.5 
		self.c_magnetom_z = (float) (self.magnetom_z - self.SENSOR_SIGN[8] * self.imumodule.M_Z_MIN) / (self.imumodule.M_Z_MAX - self.imumodule.M_Z_MIN) - self.SENSOR_SIGN[8] * 0.5 
	
		## Tilt compensated Magnetic filed X:
		MAG_X = self.c_magnetom_x * cos_pitch + self.c_magnetom_y * sin_roll * sin_pitch + self.c_magnetom_z * cos_roll * sin_pitch 
		## Tilt compensated Magnetic filed Y:
		MAG_Y = self.c_magnetom_y * cos_roll - self.c_magnetom_z * sin_roll 
		## Magnetic Heading
		self.MAG_Heading = math.atan2(-MAG_Y, MAG_X) 

	def Gyro_Scaled_X(self, x):
		return ((x) * self.ToRad(self.Gyro_Gain_X)) ##Return the scaled ADC raw data of the gyro in radians for second
	
	def Gyro_Scaled_Y(self, x):
		return ((x) * self.ToRad(self.Gyro_Gain_Y)) ##Return the scaled ADC raw data of the gyro in radians for second
	
	def Gyro_Scaled_Z(self, x):
		return ((x) * self.ToRad(self.Gyro_Gain_Z)) ##Return the scaled ADC raw data of the gyro in radians for second
	
	def ToRad(self, x):
		return ((x) * (math.pi / 180))  ## *pi/180
	
	def ToDeg(self, x):
		return ((x) * (180 / math.pi))  ## *180/pi

	def constrain(self, val, low, high):
		if (val < low):
			return low
		elif (val > high):
			return high
		else:
			return val
		
	def output_array(self):
		roll_degr = self.ToDeg(self.roll)
		pitch_degr = self.ToDeg(self.pitch)
		yaw_degr = self.ToDeg(self.yaw)
		return_array = (roll_degr, pitch_degr, yaw_degr)
		return return_array