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
#include <math.h>

//#include <pololu/orangutan.h>

#include "MinIMU9AHRS.h"
#include "vector.h"
#include "matrix.h"

/**************************************************/
void Normalize(void)
{

}

/**************************************************/
void Drift_correction(void)
{

}
/**************************************************/
/*
 void Accel_adjust(void)
 {
 Accel_Vector[1] += Accel_Scale(speed_3d*Omega[2]);  // Centrifugal force on Acc_y = GPS_speed*GyroZ
 Accel_Vector[2] -= Accel_Scale(speed_3d*Omega[1]);  // Centrifugal force on Acc_z = GPS_speed*GyroY
 }
 */
/**************************************************/

void Matrix_update(void)
{

}

void Euler_angles(void)
{
	pitch = -asin(DCM_Matrix[2][0]);
	roll = atan2(DCM_Matrix[2][1], DCM_Matrix[2][2]);
	yaw = atan2(DCM_Matrix[1][0], DCM_Matrix[0][0]);
}

