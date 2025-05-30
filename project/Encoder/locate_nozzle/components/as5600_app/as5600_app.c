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
#include "driver/uart.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "as5600_dev.h"
#include "as5600_app.h"

static const char *TAG = "as5600_app";
TaskHandle_t as5600_app_task_Handle;
#define I2C_MASTER_SCL0_IO           (GPIO_NUM_5)      /*!< GPIO number used for I2C master clock */
#define I2C_MASTER_SDA0_IO           (GPIO_NUM_6)      /*!< GPIO number used for I2C master data  */
#define I2C_MASTER_NUM0              0                          /*!< I2C master i2c port number, the number of i2c peripheral interfaces available will depend on the chip */
#define I2C_MASTER_SCL1_IO           (GPIO_NUM_7)      /*!< GPIO number used for I2C master clock */
#define I2C_MASTER_SDA1_IO           (GPIO_NUM_8)      /*!< GPIO number used for I2C master data  */
#define I2C_MASTER_NUM1              1                          /*!< I2C master i2c port number, the number of i2c peripheral interfaces available will depend on the chip */


#define AS600_SENSOR_ADDR                 0x36        
#define AS5600_ANGLE_H           0x0e      
#define AS5600_ANGLE_L           0x0f
#define AS5600_MAX_VALUE         4096

#define ORIGIN_COORDINATES_X     335
#define ORIGIN_COORDINATES_Y     1866
#define RESOLUTION_RATIO         255.85
static as5600_data as5600_data0,as5600_data1;
static int64_t as5600_time;

static struct Nozzle
{
    //绝对坝标
    double x; 
    double y;
    //累计坘化�?
    int delta_A;
    int delta_B;
}nozzle;

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

void as5600_app_dev_measure(as5600_data *data){
    data->angle = as5600_get_angle(data->value);
    data->direction = as5600_get_dir(data->value - data->last_value);
    data->circle = as5600_get_circle(data->direction,data->circle);
    
    // data->totol_angle = as5600_get_total_angle(data->value,data->circle);
    data->total_value = as5600_get_total_value(data->value,data->circle,data->init_total_value);
    

    // ESP_LOGI(TAG, "angle:%f dir:%d circle:%d total:%.2f",data->angle,data->direction,data->circle,data->totol_angle);
}
void as5600_app_monitor(){
    // ESP_LOGI(TAG,"%d,%d,%d,%d|||%d,%d,%f,%f"
    //         ,as5600_data0.total_value,as5600_data0.last_total_value
    //         ,as5600_data1.total_value,as5600_data1.last_total_value
    //         ,nozzle.delta_A,nozzle.delta_B,nozzle.x,nozzle.y);
    ESP_LOGI(TAG,"%d,%d,%d,%d|||%d,%d,%d,%d    ||%f,%f"
            ,as5600_data0.value,as5600_data0.total_value,as5600_data0.direction,as5600_data0.circle
            ,as5600_data1.value,as5600_data1.total_value,as5600_data1.direction,as5600_data1.circle
            ,nozzle.x,nozzle.y);
}
void as5600_app_vofa_monitor(){
    // printf("%lld\n"
    // ,as5600_time);
    // printf("%lld,%d,%d\n"
    // ,as5600_time
    // ,as5600_data0.total_value
    // ,as5600_data1.total_value
    // );
    printf("%lld,%d,%d,%d,%d\n"
    ,as5600_time
    ,as5600_data0.value,as5600_data0.total_value
    ,as5600_data1.value,as5600_data1.total_value
    );
}
void as5600_app_get_coordinate(as5600_data *data0, as5600_data *data1){
    nozzle.delta_A = data0->total_value - data0->last_total_value;
    nozzle.delta_B = data1->total_value - data1->last_total_value;

    // if(abs(nozzle.delta_A)<60 && abs(nozzle.delta_A-data0->delta)>150){
    //     ESP_LOGE("A","[%d, %d]",nozzle.delta_A,data0->delta);
    // }
    // if(abs(nozzle.delta_B)<60 && abs(nozzle.delta_B-data1->delta)>150){
    //     ESP_LOGE("B","[%d, %d]",nozzle.delta_B,data1->delta);
    // }
    int delta_x = (nozzle.delta_A + nozzle.delta_B);
    int delta_y = (nozzle.delta_A - nozzle.delta_B);
    nozzle.x = nozzle.x - (double)delta_x/RESOLUTION_RATIO;
    nozzle.y = nozzle.y - (double)delta_y/RESOLUTION_RATIO;
    // ESP_LOGE(TAG,"dir:[%d, %d], total:[%d,%d], value:[%d,%d]",
    //                 delta_x,delta_y,nozzle.delta_A,nozzle.delta_B,
    //                 data0->value-data0->last_value,data1->value-data1->last_value)
    // printf("%d,%d,%d,%d,%d,%d\n",
    //                 delta_x,delta_y,nozzle.delta_A,nozzle.delta_B,
    //                 data0->value-data0->last_value,data1->value-data1->last_value);
    data0->last_total_value = data0->total_value;
    data1->last_total_value = data1->total_value;
    data0->delta = nozzle.delta_A;
    data1->delta = nozzle.delta_B;
    data0->last_value = data0->value;
    data1->last_value = data1->value;
    
}
void as5600_time_interval(){
    static int64_t now_time;
    printf("interval:%lld\n",esp_timer_get_time()-now_time);
    now_time = esp_timer_get_time();
}
void as5600_app_task(void *arg){
    // as5600_data0.last_value = as5600_dev_iic0_read();
    // as5600_data0.init_total_value = as5600_data0.last_value;
    // as5600_data1.last_value = as5600_dev_iic1_read();
    // as5600_data1.init_total_value = as5600_data1.last_value;
    // nozzle.x = 0;
    // nozzle.y = 0;
    // ESP_LOGW(TAG,"init:init_value:%d,%d init_total_value:%d,%d"
    //             ,as5600_data0.init_value,as5600_data1.init_value
    //             ,as5600_data0.init_total_value,as5600_data1.init_total_value);
    while (1){
        as5600_time = esp_timer_get_time();
        as5600_data0.value = as5600_dev_iic0_read();
        as5600_data1.value = as5600_dev_iic1_read();
        as5600_app_dev_measure(&as5600_data0);
        as5600_app_dev_measure(&as5600_data1);
        as5600_app_get_coordinate(&as5600_data0,&as5600_data1);
        // int64_t as5600_time_ = esp_timer_get_time();
        // printf("%lld\n",as5600_time_-as5600_time);
        // as5600_app_monitor();
        
        as5600_app_vofa_monitor();
        // as5600_time_interval();
        // printf("as5600:%d,%d,%d,%d\n",
        // as5600_data0.value,as5600_data1.value,as5600_data0.total_value,as5600_data1.total_value);
        // printf("value0:%d,total0:%d,value1:%d,total1:%d\n",
        // as5600_data0.value,as5600_data0.total_value,as5600_data1.value,as5600_data1.total_value);
        vTaskDelay(10 / portTICK_PERIOD_MS);
    }
}

void as5600_app_measure(){
    as5600_time = esp_timer_get_time();
    as5600_data0.value = as5600_dev_iic0_read();
    as5600_data1.value = as5600_dev_iic1_read();
    as5600_app_dev_measure(&as5600_data0);
    as5600_app_dev_measure(&as5600_data1);
    as5600_app_get_coordinate(&as5600_data0,&as5600_data1);
    as5600_app_vofa_monitor();
}

void as5600_app_task_creat(void){
    xTaskCreate(as5600_app_task, "as5600_app_task", 1024*3, NULL, configMAX_PRIORITIES-1, &as5600_app_task_Handle);
}

void as5600_app_init(){
    as5600_dev_init();
    as5600_data0.last_value = as5600_dev_iic0_read();
    as5600_data0.init_total_value = as5600_data0.last_value;
    as5600_data1.last_value = as5600_dev_iic1_read();
    as5600_data1.init_total_value = as5600_data1.last_value;
    nozzle.x = 0;
    nozzle.y = 0;
    ESP_LOGW(TAG,"init:init_value:%d,%d init_total_value:%d,%d"
                ,as5600_data0.init_value,as5600_data1.init_value
                ,as5600_data0.init_total_value,as5600_data1.init_total_value);
    ESP_LOGI(TAG, "AS5600 I2C initialized successfully");
    // as5600_app_task_creat(); 
}