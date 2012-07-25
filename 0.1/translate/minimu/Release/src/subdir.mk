################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../src/Compass.c \
../src/DCM.c \
../src/I2C.c \
../src/MinIMU9AHRS.c \
../src/Output.c \
../src/Vector.c \
../src/cr_startup_lpc17.c \
../src/matrix.c 

OBJS += \
./src/Compass.o \
./src/DCM.o \
./src/I2C.o \
./src/MinIMU9AHRS.o \
./src/Output.o \
./src/Vector.o \
./src/cr_startup_lpc17.o \
./src/matrix.o 

C_DEPS += \
./src/Compass.d \
./src/DCM.d \
./src/I2C.d \
./src/MinIMU9AHRS.d \
./src/Output.d \
./src/Vector.d \
./src/cr_startup_lpc17.d \
./src/matrix.d 


# Each subdirectory must supply rules for building sources it contributes
src/%.o: ../src/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: MCU C Compiler'
	arm-none-eabi-gcc -DNDEBUG -D__CODE_RED -D__USE_CMSIS=CMSISv1p30_LPC17xx -D__NEWLIB__ -I"E:\mbuckley_data\ARM\LPCXpresso_4.1.5_219.workspace\Lib_MCU\inc" -I"E:\mbuckley_data\ARM\LPCXpresso_4.1.5_219.workspace\Lib_EaBaseBoard\inc" -I"E:\mbuckley_data\ARM\LPCXpresso_4.1.5_219.workspace\Lib_CMSISv1p30_LPC17xx\inc" -O3 -Os -g -Wall -c -fmessage-length=0 -fno-builtin -ffunction-sections -fdata-sections -mcpu=cortex-m3 -mthumb -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '

src/cr_startup_lpc17.o: ../src/cr_startup_lpc17.c
	@echo 'Building file: $<'
	@echo 'Invoking: MCU C Compiler'
	arm-none-eabi-gcc -D__NEWLIB__ -DNDEBUG -D__CODE_RED -D__USE_CMSIS=CMSISv1p30_LPC17xx -I"E:\mbuckley_data\ARM\LPCXpresso_4.1.5_219.workspace\Lib_MCU\inc" -I"E:\mbuckley_data\ARM\LPCXpresso_4.1.5_219.workspace\Lib_EaBaseBoard\inc" -I"E:\mbuckley_data\ARM\LPCXpresso_4.1.5_219.workspace\Lib_CMSISv1p30_LPC17xx\inc" -O3 -Os -g -Wall -c -fmessage-length=0 -fno-builtin -ffunction-sections -fdata-sections -mcpu=cortex-m3 -mthumb -MMD -MP -MF"$(@:%.o=%.d)" -MT"src/cr_startup_lpc17.d" -o"$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


