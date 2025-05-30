#include <stdint.h>
#include <stdio.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/stream_buffer.h"
#include "esp_log.h"
#include "esp_timer.h"

#include "algorithm_app.h"

uint8_t algorithm_app_stable_speed(float speed,int up, int ld, uint8_t th){
    static int s_times=0;
    float temp = fabs(speed);
    // if((temp>up && temp<ld) || (temp>2*up && temp<2*ld))
    if(temp>up && temp<ld)
        s_times++;
    if(s_times>th){
        s_times = 0;
        return 1;
    }
    return 0;
}