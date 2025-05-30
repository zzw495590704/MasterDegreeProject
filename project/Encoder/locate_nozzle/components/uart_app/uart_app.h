#ifndef __UART_APP_H__
#define __UART_APP_H__

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "as5600_app.h"
#include "uart_dev.h"

#ifdef __cplusplus
extern "C" {
#endif

void uart_app_init();

#ifdef __cplusplus
}
#endif
#endif