################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include subdir.mk
-include src/subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 

# All Target
all: MinIMU9AHRS.axf

# Tool invocations
MinIMU9AHRS.axf: $(OBJS) $(USER_OBJS)
	@echo 'Building target: $@'
	@echo 'Invoking: MCU Linker'
	arm-none-eabi-gcc -nostdlib -L"E:\mbuckley_data\ARM\LPCXpresso_4.1.5_219.workspace\Lib_CMSISv1p30_LPC17xx\Release" -L"E:\mbuckley_data\ARM\LPCXpresso_4.1.5_219.workspace\Lib_MCU\Release" -L"E:\mbuckley_data\ARM\LPCXpresso_4.1.5_219.workspace\Lib_EaBaseBoard\Release" -Xlinker -Map=MinIMU9AHRS.map -Xlinker --gc-sections -mcpu=cortex-m3 -mthumb -T "MinIMU9AHRS_Release.ld" -o"MinIMU9AHRS.axf" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '
	$(MAKE) --no-print-directory post-build

# Other Targets
clean:
	-$(RM) $(OBJS)$(C_DEPS)$(EXECUTABLES) MinIMU9AHRS.axf
	-@echo ' '

post-build:
	-@echo 'Performing post-build steps'
	-arm-none-eabi-size MinIMU9AHRS.axf; # arm-none-eabi-objcopy -O binary MinIMU9AHRS.axf MinIMU9AHRS.bin ; checksum -p LPC1769 -d MinIMU9AHRS.bin;
	-@echo ' '

.PHONY: all clean dependents
.SECONDARY: post-build

-include ../makefile.targets
