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

//#include <pololu/orangutan.h>

#include "MinIMU9AHRS.h"
#include "Output.h"

#include "lpc17xx_i2c.h"

#define I2CDEV LPC_I2C2

#define ACCEL_I2C_ADDR		(0x18)
#define GYRO_I2C_ADDR		(0x69)
#define	COMPASS_I2C_ADDR	(0x1E)

#define	L3G4200D_CTRL_REG1	0x20
#define	L3G4200D_CTRL_REG4	0x23
#define L3G4200D_OUT_X_L_A	0x28
#define LSM303_CTRL_REG1_A	0x20
#define LSM303_CTRL_REG4_A	0x23
#define LSM303_OUT_X_L_A	0x28
#define	LSM303_OUTXH_M		0x03
#define LSM303_MR_REG_M		0x02

static int i2c_read(uint8_t addr, uint8_t* buf, uint32_t len)
{
	I2C_M_SETUP_Type rxsetup;

	rxsetup.sl_addr7bit = addr;
	rxsetup.tx_data = NULL; // Get address to read at writing address
	rxsetup.tx_length = 0;
	rxsetup.rx_data = buf;
	rxsetup.rx_length = len;
	rxsetup.retransmissions_max = 3;

	if (I2C_MasterTransferData(I2CDEV, &rxsetup, I2C_TRANSFER_POLLING) == SUCCESS)
	{
		return (0);
	}
	else
	{
		print_line("I2C Read Error");
		return (-1);
	}
}

static int i2c_write(uint8_t addr, uint8_t* buf, uint32_t len)
{
	I2C_M_SETUP_Type txsetup;

	txsetup.sl_addr7bit = addr;
	txsetup.tx_data = buf;
	txsetup.tx_length = len;
	txsetup.rx_data = NULL;
	txsetup.rx_length = 0;
	txsetup.retransmissions_max = 3;

	if (I2C_MasterTransferData(I2CDEV, &txsetup, I2C_TRANSFER_POLLING) == SUCCESS)
	{
		return (0);
	}
	else
	{
		print_line("I2C Write Error");
		return (-1);
	}
}

void i2c_init()
{
	PINSEL_CFG_Type PinCfg;

	/* Initialize I2C2 pin connect */
	PinCfg.Funcnum = 2;
	PinCfg.Pinnum = 10;
	PinCfg.Portnum = 0;
	PINSEL_ConfigPin(&PinCfg);
	PinCfg.Pinnum = 11;
	PINSEL_ConfigPin(&PinCfg);

	// Initialize I2C peripheral
	I2C_Init(I2CDEV, 100000);

	/* Enable I2C1 operation */
	I2C_Cmd(I2CDEV, ENABLE);
}

void Gyro_Init()
{
	//	gyro.writeReg(L3G4200D_CTRL_REG1, 0x0F); // normal power mode, all axes enabled, 100 Hz
	//	gyro.writeReg(L3G4200D_CTRL_REG4, 0x20); // 2000 dps full scale

	uint8_t buf[2];

	buf[0] = L3G4200D_CTRL_REG1;
	buf[1] = 0x0F;
	i2c_write(GYRO_I2C_ADDR, buf, 2);

	buf[0] = L3G4200D_CTRL_REG4;
	buf[1] = 0x20;
	i2c_write(GYRO_I2C_ADDR, buf, 2);
}

void Read_Gyro()
{
	uint8_t buf[6];

	buf[0] = L3G4200D_OUT_X_L_A | 0x80;
	i2c_write(GYRO_I2C_ADDR, buf, 1);
	i2c_read(GYRO_I2C_ADDR, buf, 6);
	unsigned char gxl = buf[0];
	unsigned char gxh = buf[1];
	unsigned char gyl = buf[2];
	unsigned char gyh = buf[3];
	unsigned char gzl = buf[4];
	unsigned char gzh = buf[5];

	AN[0] = (short int)(gxh << 8 | gxl);
	AN[1] = (short int)(gyh << 8 | gyl);
	AN[2] = (short int)(gzh << 8 | gzl);
	gyro_x = SENSOR_SIGN[0] * (AN[0] - AN_OFFSET[0]);
	gyro_y = SENSOR_SIGN[1] * (AN[1] - AN_OFFSET[1]);
	gyro_z = SENSOR_SIGN[2] * (AN[2] - AN_OFFSET[2]);
}

void Accel_Init()
{
	//	compass.writeAccReg(LSM303_CTRL_REG1_A, 0x27); // normal power mode, all axes enabled, 50 Hz
	//	compass.writeAccReg(LSM303_CTRL_REG4_A, 0x30); // 8 g full scale

	uint8_t buf[2];

	buf[0] = LSM303_CTRL_REG1_A;
	buf[1] = 0x27;
	i2c_write(ACCEL_I2C_ADDR, buf, 2);

	buf[0] = LSM303_CTRL_REG4_A;
	buf[1] = 0x30;
	i2c_write(ACCEL_I2C_ADDR, buf, 2);
}

void Read_Accel()
{
	uint8_t buf[6];

	buf[0] = LSM303_OUT_X_L_A | 0x80;
	i2c_write(ACCEL_I2C_ADDR, buf, 1);
	i2c_read(ACCEL_I2C_ADDR, buf, 6);
	unsigned char axl = buf[0];
	unsigned char axh = buf[1];
	unsigned char ayl = buf[2];
	unsigned char ayh = buf[3];
	unsigned char azl = buf[4];
	unsigned char azh = buf[5];

	AN[3] = ((short int)(axh << 8 | axl) >> 4);
	AN[4] = ((short int)(ayh << 8 | ayl) >> 4);
	AN[5] = ((short int)(azh << 8 | azl) >> 4);
	accel_x = SENSOR_SIGN[3] * (AN[3] - AN_OFFSET[3]);
	accel_y = SENSOR_SIGN[4] * (AN[4] - AN_OFFSET[4]);
	accel_z = SENSOR_SIGN[5] * (AN[5] - AN_OFFSET[5]);
}

void Compass_Init()
{
	//	compass.writeMagReg(LSM303_MR_REG_M, 0x00); // continuous conversion mode
	// 15 Hz default
	uint8_t buf[2];

	buf[0] = LSM303_MR_REG_M;
	buf[1] = 0x00;
	i2c_write(COMPASS_I2C_ADDR, buf, 2);
}

void Read_Compass()
{
	uint8_t buf[6];

	buf[0] = LSM303_OUTXH_M;
	i2c_write(COMPASS_I2C_ADDR, buf, 1);
	i2c_read(COMPASS_I2C_ADDR, buf, 6);
	unsigned char mxh = buf[0];
	unsigned char mxl = buf[1];
	unsigned char mzh = buf[2]; // LSM303DLM z is before y
	unsigned char mzl = buf[3];
	unsigned char myh = buf[4];
	unsigned char myl = buf[5];

	magnetom_x = SENSOR_SIGN[6] * (short int)(mxh << 8 | mxl);
	magnetom_y = SENSOR_SIGN[7] * (short int)(myh << 8 | myl);
	magnetom_z = SENSOR_SIGN[8] * (short int)(mzh << 8 | mzl);
}

