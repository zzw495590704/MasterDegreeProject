#include "uart_app.h"
static const char *TAG = "uart_app";
TaskHandle_t sensor_app_task_Handle;
uint8_t send_cmd[][2] = {
    {0xa3,0x0d}
};
int uart_app_interactive(void){
    uint8_t data[5];
    uint16_t buf_len = uart_dev_recive(data,2,500);
    if (memcmp(send_cmd[0], data, sizeof(send_cmd[0])) == 0) {
        printf("Arrays are equal\n");
        // uart_dev_delete_buffer();
    } 
    // uart_dev_send(senser_cmd[0],5);
    // ESP_LOG_BUFFER_HEX("setting_sensor_return",data,buf_len);
    // int weight = data[4]<<16 | data[5]<<8 | data[6];
    // if (data[3]==0x01){
    //     weight *= -1; 
    // }
    // ESP_LOGI(TAG,"weight:%d",weight);
    return 0;
}

void uart_app_task(){
    while (1)
    {
       uart_app_interactive();
    }
    
}

//  void sensor_app_task(void *arg){
//     while (1){
//         sensor_app_read_weight();
//         vTaskDelay(1000 / portTICK_PERIOD_MS);
//     }
//     vTaskDelete(sensor_app_task_Handle);
//  }

void uart_app_task_creat(void){
    xTaskCreate(uart_app_task, "uart_app_task", 1024*3, NULL, configMAX_PRIORITIES-1, &sensor_app_task_Handle);
}


void uart_app_init(){
    uart_dev_init();
    uart_app_task_creat();
}