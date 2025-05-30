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

static as5600_data as5600_data0;
static int64_t as5600_time;


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
// ????????
double as5600_predict_weight(double x) {
    double coefficient = 5.85353152e-06;
    double intercept = -0.0742029745713122;
    return coefficient * x + intercept;
}
void as5600_app_handle_data(as5600_data *data){
    data->direction = as5600_get_dir(data->value - data->last_value);
    data->circle = as5600_get_circle(data->direction,data->circle);
    data->total_value = as5600_get_total_value(data->value,data->circle,data->init_total_value);
    data->last_value = data->value;
    // data->weight = as5600_predict_weight(data->total_value);
}
void as5600_app_monitor(){
    // ESP_LOGI(TAG,"%d,%d,%d,%d|||%d,%d,%f,%f"
    //         ,as5600_data0.total_value,as5600_data0.last_total_value
        //         ,as5600_data1.total_value,as5600_data1.last_total_value
    //         ,nozzle.delta_A,nozzle.delta_B,nozzle.x,nozzle.y);
   
}
void as5600_app_vofa_monitor(){
    // printf("%lld\n"
    // ,as5600_time);
    // printf("%lld,%d,%d\n"
    // ,as5600_time
    // ,as5600_data0.total_value
    // ,as5600_data1.total_value
    // );
    printf("%lld,%d,%d\n"
    ,as5600_time
    ,as5600_data0.value,as5600_data0.total_value
    );
}

void as5600_time_interval(){
    static int64_t now_time;
    printf("interval:%lld\n",esp_timer_get_time()-now_time);
    now_time = esp_timer_get_time();
}

void as5600_app_measure(){
    as5600_time = esp_timer_get_time();
    as5600_data0.value = as5600_dev_iic0_read();
    as5600_app_handle_data(&as5600_data0);
    as5600_app_vofa_monitor();
}


void as5600_app_init(){
    as5600_dev_init();
    as5600_data0.last_value = as5600_dev_iic0_read();
    as5600_data0.init_total_value = as5600_data0.last_value;

    ESP_LOGI(TAG, "AS5600 I2C initialized successfully");
}