/*
 * I2C.h
 *
 *  Created on: Jan 8, 2012
 *      Author: mbuckley
 */

#ifndef I2C_H_
#define I2C_H_

extern void i2c_init();
extern void Gyro_Init();
extern void Read_Gyro();
extern void Accel_Init();
extern void Read_Accel();
extern void Compass_Init();
extern void Read_Compass();

#endif /* I2C_H_ */
