#ifndef __LEDC_APP_H__
#define __LEDC_APP_H__

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

#ifdef __cplusplus
extern "C" {
#endif

void ledc_app_init();

#ifdef __cplusplus
}
#endif
#endif