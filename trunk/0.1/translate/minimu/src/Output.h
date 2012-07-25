/*
 * Output.h
 *
 *  Created on: Jan 8, 2012
 *      Author: mbuckley
 */

#ifndef OUTPUT_H_
#define OUTPUT_H_

extern void init_uart(void);
extern void print_line(char* str);
extern void print_number(int num);
extern void print_str(char* str);
extern void printdata(void);

#endif /* OUTPUT_H_ */
