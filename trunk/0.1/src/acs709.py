'''
Created on Jul 17, 2012

@author: Peter Hendriks

Usage:
import acs709
mm = acs709.acs709(minimaestro, port)
'''

from threading import Thread
import time

class acs709(Thread):
	'''
	Current sensor ACS709 from Pololu. The module is a single thread. The thread will compute Ampere usage and convert to mAh used.
	There will be a setting to give battery charge, the module will calculate the time until depletion guessed on avarage usage.

	Output of the ACS709 isto +- 2% accurate. Together with calculation error 10% safety is built in for depletion time.
	'''

	def __init__(self, minimaestro, port):
		self.minimaestro = minimaestro
		self.port = port
		self.time = 0.0 # time
		self.old_time = 0.0
		self.delta = 0.0 # delta time
		self.mah = 0.0 # mAh usage
		self.battery = 0.0 # mAh in battery
		Thread.__init__(self)

	def run():
		self.running = 1
		while self.running:
			self.old_time = self.time
			self.time = time.time()			
			self.delta = self.time - self.old_time			
			self.get_current_usage()
			self.calculate_totals()

			if (self.delta < 0.1):
				sleeptime = 0.1 - self.delta
				time.sleep(sleeptime)


	def get_current_usage(self):
		voltage = self.minimaestro.get_voltage(self.port)
	
	def stop(self):
		self.running = 0
		
	def decode_voltage(self, voltage):
		'''
		Calculation:
		VIOUT = (0.028 V / A * i + 2.5 V) * VCC / 5 V
		VIOUT = (0.028 * i + 2.5) * VCC / 5 # VCC = 5
		VIOUT =  + 2.5
		VIOUT - 2.5 = 0.028 * i
		i = (VIOUT - 2.5) / 0.028
		'''		
		A = (voltage - 2.5) / 0.028
		return A
