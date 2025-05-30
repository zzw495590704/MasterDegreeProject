#ifndef __SENSOR_APP_H
#define __SENSOR_APP_H

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "stdint.h"
#include <time.h>
#include <sys/time.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

#include "driver/i2c.h"

enum AS5600_DIR_ENUM{
    AS5600_STOP = 0,
    AS5600_TURN_N = 1,
    AS5600_TURN_P = 2,
    AS5600_TURN_N_OVER = 3,
    AS5600_TURN_P_OVER = 4,
};
typedef struct 
{
    int i2c_port;
    int SDA_IO;
    int SCL_IO;
}as5600_dev;


void as5600_dev_init();
uint16_t as5600_dev_iic0_read();
uint16_t as5600_dev_iic1_read();
#endif

