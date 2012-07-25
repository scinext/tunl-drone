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
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "MinIMU9AHRS.h"

#include "lpc17xx_uart.h"

#define UART_DEV LPC_UART3

void init_uart(void)
{
	PINSEL_CFG_Type PinCfg;
	UART_CFG_Type uartCfg;

	/* Initialize UART3 pin connect */
	PinCfg.Funcnum = 2;
	PinCfg.Pinnum = 0;
	PinCfg.Portnum = 0;
	PINSEL_ConfigPin(&PinCfg);
	PinCfg.Pinnum = 1;
	PINSEL_ConfigPin(&PinCfg);

	uartCfg.Baud_rate = 115200;
	uartCfg.Databits = UART_DATABIT_8;
	uartCfg.Parity = UART_PARITY_NONE;
	uartCfg.Stopbits = UART_STOPBIT_1;

	UART_Init(UART_DEV, &uartCfg);

	UART_TxCmd(UART_DEV, ENABLE);

}

void print_str(char* str)
{
    UART_SendString(UART_DEV, (uint8_t*)str);
}

void print_line(char* str)
{
	static char* crlf = "\r\n";

	print_str(str);
    UART_SendString(UART_DEV, (uint8_t*)crlf);
}

void itoa(unsigned int num, char *buf, unsigned int base)
{
	sprintf(buf, "%d", num);
}

void print_number(int num)
{
	char buf[6];
	itoa(num, buf, 10);
	print_line(buf);
}

long convert_to_dec(float x)
{
	return x * 10000000;
}

void printdata(void)
{
	char str[200];

#if PRINT_EULER == 1
	sprintf(str, "!ANG:% 3.1f,% 3.1f,% 3.1f", (double)ToDeg(roll), (double)ToDeg(pitch), (double)ToDeg(yaw));
    UART_SendString(UART_DEV, (uint8_t*)str);
#endif
#if PRINT_ANALOGS==1
	sprintf(str, ",AN:% 5d,% 5d,% 5d,% 5d,% 5d,% 5d,% 4.1f,% 4.1f,% 4.1f",
			AN[0],AN[1],AN[2],AN[3],AN[4],AN[5], (double)c_magnetom_x, (double)c_magnetom_y, (double)c_magnetom_z);
    UART_SendString(UART_DEV, (uint8_t*)str);
#endif
#if PRINT_DCM == 1
	sprintf(str, ",DCM: % 2.0f,% 2.0f,% 2.0f,% 2.0f,% 2.0f,% 2.0f,% 2.0f,% 2.0f,% 2.0f",
			(double)DCM_Matrix[0][0],(double)DCM_Matrix[0][1],(double)DCM_Matrix[0][2],
			(double)DCM_Matrix[1][0],(double)DCM_Matrix[1][1],(double)DCM_Matrix[1][2],
			(double)DCM_Matrix[2][0],(double)DCM_Matrix[2][1],(double)DCM_Matrix[2][2]);
    UART_SendString(UART_DEV, (uint8_t*)str);
#endif
	static char* crlf = "\r\n";
    UART_SendString(UART_DEV, (uint8_t*)crlf);
}


