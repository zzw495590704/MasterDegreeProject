/* UART Events Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/

#include "stdint.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/stream_buffer.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "as5600_dev.h"
#include "as5600_app.h"
#include "algorithm_app.h"
static const char *TAG = "as5600_app";
TaskHandle_t as5600_app_task_Handle;
#define I2C_MASTER_SCL0_IO           (GPIO_NUM_5)      /*!< GPIO number used for I2C master clock */
#define I2C_MASTER_SDA0_IO           (GPIO_NUM_6)      /*!< GPIO number used for I2C master data  */
#define I2C_MASTER_NUM0              0                          /*!< I2C master i2c port number, the number of i2c peripheral interfaces available will depend on the chip */


#define AS600_SENSOR_ADDR                 0x36        
#define AS5600_ANGLE_H           0x0e      
#define AS5600_ANGLE_L           0x0f
#define AS5600_MAX_VALUE         4096

#define RESOLUTION_RATIO         127.8
#define SPEED_RATIO             60000
//2D线激光运动平台
static as5600_data laser;
//挤出机称重
static as5600_data weight;
//重量预测相关
double coefficient = 5.85353152e-06;
double intercept = -0.0742029745713122;

float as5600_get_angle(uint16_t value){
    float angle;
    angle=((int) value & 0b0000111111111111)*360.0/4096.0;
    return angle;
}
int as5600_get_dir(int diff){
    int dir;
    //turn positve over 1 circle
    if (diff<(-1*AS5600_MAX_VALUE/2)){
        dir = AS5600_TURN_N_OVER;
    }
    //turn negative over 1 circle
    else if (diff>(AS5600_MAX_VALUE/2))
    {
        dir = AS5600_TURN_P_OVER;
    }
    else if (diff>0){
        dir = AS5600_TURN_N;
    }
    else if (diff<0){
        dir = AS5600_TURN_P;
    }
    //no turn
    else{
        dir = AS5600_STOP;
    }
    
    return dir;
}
int as5600_get_circle(int dir,int circle){
    int temp_circle = circle;
    switch (dir)
    {
    case AS5600_TURN_N_OVER:
        temp_circle += 1;
        /* code */
        break;
    case AS5600_TURN_P_OVER:
        temp_circle -= 1;
        break;
    default:
        break;
    }
    return temp_circle;
}
float as5600_get_total_angle(uint16_t value,int circle){
    float angle = as5600_get_angle(value);
    return (float)circle*360+angle;
}
int as5600_get_total_value(uint16_t value,int circle, uint16_t init_total){
    return (int)circle*4096+value - init_total;
}

float as5600_get_speed(int total, int last_total, int interval){
    float speed = (float)(total-last_total)/interval/RESOLUTION_RATIO*SPEED_RATIO;
    return speed;
}
// 定义函数来预测值
double as5600_predict_weight(double x) {
    return coefficient * x + intercept;
}
void as5600_app_task_init(){
    laser.init_total_value = as5600_dev_iic0_read();
    laser.last_value = laser.init_total_value;
    weight.init_total_value = as5600_dev_iic1_read();
    weight.last_value = laser.init_total_value;
}
void as5600_app_monitor(){
    //ESP_LOGI(TAG,"time:%lld,intervl:%d,total:%d",laser.time,laser.interval,laser.total_value);
    //ESP_LOGI(TAG,"%f",laser.speed);
    //ESP_LOGI(TAG,"total:%d  last_total:%d",laser.total_value,laser.last_total_value);
    //ESP_LOGI(TAG,"total:%d delta:%f last:%f speed:%f",laser.total_value,deltaX,deltaX_last,speed);
    printf("PRINT,%lf %d\n",weight.weight,weight.value);
}
void as5600_app_vofa_monitor(){
    printf("PRINT:%lf\n",laser.speed);
}

void as5600_app_measure_speed(as5600_data *data){
    data->direction = as5600_get_dir(data->value - data->last_value);
    data->circle = as5600_get_circle(data->direction,data->circle);
    data->total_value = as5600_get_total_value(data->value,data->circle,data->init_total_value);
    data->speed = as5600_get_speed(data->total_value,data->last_total_value,data->interval);
    data->last_value = data->value;
    data->last_total_value = data->total_value;
}

void as5600_app_measure_weight(as5600_data *data){
    data->direction = as5600_get_dir(data->value - data->last_value);
    data->circle = as5600_get_circle(data->direction,data->circle);
    data->total_value = as5600_get_total_value(data->value,data->circle,data->init_total_value);
    data->weight =  as5600_predict_weight(data->total_value);
    data->last_value = data->value;
    data->last_total_value = data->total_value;
}


void as5600_app_task(void *arg){
    as5600_app_task_init();
    while (1){
        laser.interval = (esp_timer_get_time()-laser.time)/1000;
        laser.time = esp_timer_get_time();
        laser.value = as5600_dev_iic0_read();
        weight.value = as5600_dev_iic1_read();
        as5600_app_measure_speed(&laser);
        as5600_app_measure_weight(&weight);
        //printf("%d,%d,%lf\n",weight.value,weight.total_value,weight.weight);
        if (algorithm_app_stable_speed(laser.speed,220,270,2))
        {
            printf("SCAN:%lf\n",weight.weight);
        }
        else{
            // as5600_app_monitor();
            as5600_app_vofa_monitor();
        }
        vTaskDelay(30 / portTICK_PERIOD_MS);
    }
}

void as5600_app_task_creat(void){
    xTaskCreate(as5600_app_task, "as5600_app_task", 1024*3, NULL, configMAX_PRIORITIES-1, &as5600_app_task_Handle);
}

void as5600_app_init(){
    as5600_dev_init();
    ESP_LOGI(TAG, "AS5600 I2C initialized successfully");
    as5600_app_task_creat(); 
}