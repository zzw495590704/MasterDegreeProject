#ifndef __ALOGRITHNM_APP_H__
#define __ALOGRITHNM_APP_H__

#include <stdio.h>
#include <string.h>
#include "driver/gpio.h"
#ifdef __cplusplus
extern "C" {
#endif

uint8_t algorithm_app_stable_speed(float speed,int up, int ld, uint8_t th);

#ifdef __cplusplus
}
#endif
#endif