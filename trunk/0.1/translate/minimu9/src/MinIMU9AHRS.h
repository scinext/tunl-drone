/*
 * MinIMU9AHRS.h
 *
 *  Created on: Jan 7, 2012
 *      Author: mbuckley
 */

#ifndef MINIMU9AHRS_H_
#define MINIMU9AHRS_H_

#ifdef __USE_CMSIS
#include "LPC17xx.h"
#endif

#include <cr_section_macros.h>
#include <NXP/crp.h>

#include "lpc17xx_pinsel.h"
#include "lpc17xx_gpio.h"
#include "lpc17xx_timer.h"

#define constrain(amt,low,high) ((amt)<(low)?(low):((amt)>(high)?(high):(amt)))

//OUTPUTMODE=1 will print the corrected data,
//OUTPUTMODE=0 will print uncorrected data of the gyros (with drift)
#define OUTPUTMODE 1

#define PRINT_DCM 0     //Will print the whole direction cosine matrix
#define PRINT_ANALOGS 0 //Will print the analog raw data
#define PRINT_EULER 1   //Will print the Euler angles Roll, Pitch and Yaw

#define ToRad(x) ((x)*0.01745329252)  // *pi/180
#define ToDeg(x) ((x)*57.2957795131)  // *180/pi

#define GRAVITY 256  //this equivalent to 1G in the raw data coming from the accelerometer

// L3G4200D gyro: 2000 dps full scale
// 70 mdps/digit; 1 dps = 0.07
#define Gyro_Gain_X 0.07 //X axis Gyro gain
#define Gyro_Gain_Y 0.07 //Y axis Gyro gain
#define Gyro_Gain_Z 0.07 //Z axis Gyro gain
#define Gyro_Scaled_X(x) ((x)*ToRad(Gyro_Gain_X)) //Return the scaled ADC raw data of the gyro in radians for second
#define Gyro_Scaled_Y(x) ((x)*ToRad(Gyro_Gain_Y)) //Return the scaled ADC raw data of the gyro in radians for second
#define Gyro_Scaled_Z(x) ((x)*ToRad(Gyro_Gain_Z)) //Return the scaled ADC raw data of the gyro in radians for second

#define Kp_ROLLPITCH 0.02
#define Ki_ROLLPITCH 0.00002
#define Kp_YAW 1.2
#define Ki_YAW 0.00002

// LSM303 magnetometer calibration constants; use the Calibrate example from
// the Pololu LSM303 library to find the right values for your board
#define M_X_MIN -712 //-796
#define M_Y_MIN -718 //-457
#define M_Z_MIN -465 //-424
#define M_X_MAX 418 //197
#define M_Y_MAX 415 //535
#define M_Z_MAX 457 //397

extern float G_Dt;    // Integration time (DCM algorithm)  We will run the integration loop at 50Hz if possible

extern int SENSOR_SIGN[9];
extern float DCM_Matrix[3][3];
extern float Update_Matrix[3][3]; //Gyros here
extern float Temporary_Matrix[3][3];

// Euler angles
extern float roll;
extern float pitch;
extern float yaw;

extern int AN[6]; //array that stores the gyro and accelerometer data
extern int AN_OFFSET[6]; //Array that stores the Offset of the sensors

extern int gyro_x;
extern int gyro_y;
extern int gyro_z;
extern int accel_x;
extern int accel_y;
extern int accel_z;
extern int magnetom_x;
extern int magnetom_y;
extern int magnetom_z;

extern float MAG_Heading;

extern float c_magnetom_x;
extern float c_magnetom_y;
extern float c_magnetom_z;

extern float Accel_Vector[3]; 	//Store the acceleration in a vector
extern float Gyro_Vector[3];	//Store the gyros turn rate in a vector
extern float Omega_Vector[3]; 	//Corrected Gyro_Vector data
extern float Omega_P[3];		//Omega Proportional correction
extern float Omega_I[3];		//Omega Integrator
extern float Omega[3];

extern float errorRollPitch[3];
extern float errorYaw[3];

#endif /* MINIMU9AHRS_H_ */
