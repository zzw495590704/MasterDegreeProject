#ifndef __AS5600_APP_H__
#define __AS5600_APP_H__

#include <stdio.h>
#include <string.h>
#include "driver/gpio.h"
#ifdef __cplusplus
extern "C" {
#endif

typedef struct 
{
    //当前位置
    uint16_t value;
    uint16_t init_value;
    uint16_t last_value;
    uint8_t direction;
    //累计位置
    int total_value;
    int last_total_value;
    int init_total_value;
    int circle;
    int delta;
    //角度换算
    float angle;
    float totol_angle;
}as5600_data;

void as5600_app_init();
void as5600_app_measure();
#ifdef __cplusplus
}
#endif
#endif