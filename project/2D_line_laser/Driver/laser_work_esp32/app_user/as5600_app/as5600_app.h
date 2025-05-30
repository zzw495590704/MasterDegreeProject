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
    uint8_t direction;
    //前一位置
    uint16_t last_value;
    int last_total_value;
    //累计位置
    int total_value;
    int init_total_value;
    int circle;
    //速度
    //TODO:修改成传感器的相对速度（目前是传动的绝对速度）,后续分离数据和传感器值
    float speed;
    double weight;
    //时间
    int64_t time;
    int interval;
}as5600_data;

void as5600_app_init();

#ifdef __cplusplus
}
#endif
#endif