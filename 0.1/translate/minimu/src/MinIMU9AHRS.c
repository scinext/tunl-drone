/*

 MinIMU-9-Arduino-AHRS
 Pololu MinIMU-9 + Arduino AHRS (Attitude and Heading Reference System)

 Copyright (c) 2011 Pololu Corporation.
 http://www.pololu.com/

 MinIMU-9-Arduino-AHRS is based on sf9domahrs by Doug Weibel and Jose Julio:
 http://code.google.com/p/sf9domahrs/

 sf9domahrs is based on ArduIMU v1.5 by Jordi Munoz and William Premerlani, Jose
 Julio and Doug Weibel:
 http://code.google.com/p/ardu-imu/

 MinIMU-9-Arduino-AHRS is free software: you can redistribute it and/or modify it
 under the terms of the GNU Lesser General Public License as published by the
 Free Software Foundation, either version 3 of the License, or (at your option)
 any later version.

 MinIMU-9-Arduino-AHRS is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
 more details.

 You should have received a copy of the GNU Lesser General Public License along
 with MinIMU-9-Arduino-AHRS. If not, see <http://www.gnu.org/licenses/>.

 */
#define	byte	unsigned char
// Uncomment the below line to use this axis definition: 
// X axis pointing forward
// Y axis pointing to the right
// and Z axis pointing down.
// Positive pitch : nose up
// Positive roll : right wing down
// Positive yaw : clockwise
int SENSOR_SIGN[9] =
{ 1, 1, 1, -1, -1, -1, 1, 1, 1 }; //Correct directions x,y,z - gyro, accelerometer, magnetometer
// Uncomment the below line to use this axis definition: 
// X axis pointing forward
// Y axis pointing to the left
// and Z axis pointing up.
// Positive pitch : nose down
// Positive roll : right wing down
// Positive yaw : counterclockwise
//int SENSOR_SIGN[9] = {1,-1,-1,-1,1,1,1,-1,-1}; //Correct directions x,y,z - gyro, accelerometer, magnetometer

// tested with Arduino Uno with ATmega328 and Arduino Duemilanove with ATMega168

#include <math.h>

//#include <pololu/orangutan.h>

#include "MinIMU9AHRS.h"
#include "I2C.h"
#include "Compass.h"
#include "DCM.h"
#include "Output.h"

float G_Dt = 0.02; // Integration time (DCM algorithm)  We will run the integration loop at 50Hz if possible

long timer = 0; //general purpuse timer
long timer_old;
long timer24 = 0; //Second timer used to print values
int AN[6]; //array that stores the gyro and accelerometer data
int AN_OFFSET[6] =
{ 0, 0, 0, 0, 0, 0 }; //Array that stores the Offset of the sensors

int gyro_x;
int gyro_y;
int gyro_z;
int accel_x;
int accel_y;
int accel_z;
int magnetom_x;
int magnetom_y;
int magnetom_z;
float c_magnetom_x;
float c_magnetom_y;
float c_magnetom_z;
float MAG_Heading;

float Accel_Vector[3] =
{ 0, 0, 0 }; //Store the acceleration in a vector
float Gyro_Vector[3] =
{ 0, 0, 0 };//Store the gyros turn rate in a vector
float Omega_Vector[3] =
{ 0, 0, 0 }; //Corrected Gyro_Vector data
float Omega_P[3] =
{ 0, 0, 0 };//Omega Proportional correction
float Omega_I[3] =
{ 0, 0, 0 };//Omega Integrator
float Omega[3] =
{ 0, 0, 0 };

// Euler angles
float roll;
float pitch;
float yaw;

float errorRollPitch[3] =
{ 0, 0, 0 };
float errorYaw[3] =
{ 0, 0, 0 };

unsigned int counter = 0;
byte gyro_sat = 0;

float DCM_Matrix[3][3] =
{
{ 1, 0, 0 },
{ 0, 1, 0 },
{ 0, 0, 1 } };
float Update_Matrix[3][3] =
{
{ 0, 1, 2 },
{ 3, 4, 5 },
{ 6, 7, 8 } }; //Gyros here


float Temporary_Matrix[3][3] =
{
{ 0, 0, 0 },
{ 0, 0, 0 },
{ 0, 0, 0 } };

void setup(void);
void loop(void);

static uint32_t msTicks = 0;

void SysTick_Handler(void) {
    msTicks++;
}

static uint32_t getTicks(void)
{
    return msTicks;
}

void delay(int ms)
{
	Timer0_Wait(ms);
}

unsigned long millis(void)
{
	return getTicks();
}

int main(void)
{
	setup();
	while(1)
	{
		loop();
	}

	return 0;
}

void halt(void)
{
	// Enter an infinite loop, just incrementing a counter
	volatile static int i = 0;
	while (1)
	{
		i++;
	}
}

void setup()
{
	// Code Red - if CMSIS 1.3 setup is being used, then SystemInit() routine
	// will be called by startup code rather than in application's main()
#ifndef __USE_CMSIS
	SystemInit(); /* initialize clocks */
#endif

	init_uart();

	if (SysTick_Config(SystemCoreClock / 1000))
	{
        print_line("SysTick_Config Failed");
		halt();
	}

	print_line("Pololu MinIMU-9 + Arduino AHRS");

	i2c_init();
	Accel_Init();
	Compass_Init();
	Gyro_Init();

	delay(2000);

	int i;
	for (i = 0; i < 32; i++) // We take some readings...
	{
		Read_Gyro();
		Read_Accel();
		int y;
		for (y = 0; y < 6; y++) // Cumulate values
			AN_OFFSET[y] += AN[y];
		delay(20);
	}

	int y;
	for (y = 0; y < 6; y++)
		AN_OFFSET[y] = AN_OFFSET[y] / 32;

	AN_OFFSET[5] -= GRAVITY * SENSOR_SIGN[5];

	print_line("Offsets");
	for (y = 0; y < 6; y++)
	{
		print_number(AN_OFFSET[y]);
	}

	timer = millis();
	delay(20);
	counter = 0;
}

void loop() //Main Loop
{
	if ((millis() - timer) >= 20) // Main loop runs at 50Hz
	{
		counter++;
		timer_old = timer;
		timer = millis();
		if (timer > timer_old)
			G_Dt = (timer - timer_old) / 1000.0; // Real time of loop run. We use this on the DCM algorithm (gyro integration time)
		else
			G_Dt = 0;

		// *** DCM algorithm
		// Data adquisition
		Read_Gyro(); // This read gyro data
		Read_Accel(); // Read I2C accelerometer

		if (counter > 5) // Read compass data at 10Hz... (5 loop runs)
		{
			counter = 0;
			Read_Compass(); // Read I2C magnetometer
			Compass_Heading(); // Calculate magnetic heading
		}

		// Calculations...
		Matrix_update();
		Normalize();
		Drift_correction();
		Euler_angles();
		// ***

		printdata();
	}

}

#ifdef __cplusplus
extern "C" void __cxa_pure_virtual()
{
	cli();
	for (;;);
}
#endif

