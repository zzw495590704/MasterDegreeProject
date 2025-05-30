#ifndef __UART_DEV_H__
#define __UART_DEV_H__

#include <stdio.h>
#include <string.h>
#include "driver/gpio.h"
#ifdef __cplusplus
extern "C" {
#endif

#define TXD_PIN (GPIO_NUM_1)
#define RXD_PIN (GPIO_NUM_2)

void uart_dev_init(void);
void uart_dev_send(const void *buf,uint16_t len);
uint16_t uart_dev_recive(void *buf,int len, uint32_t timeout_ms);
uint16_t uart_dev_recive_wait(void *buf,int len);

#ifdef __cplusplus
}
#endif
#endif