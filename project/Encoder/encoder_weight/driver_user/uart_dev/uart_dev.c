/* UART Events Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include "uart_dev.h"
#include "stdint.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/stream_buffer.h"
#include "driver/uart.h"
#include "esp_log.h"
#include "esp_timer.h"

static const char *TAG = "uart_events";
// static const int RX_BUF_SIZE = 1024;
StreamBufferHandle_t s_uart_steam_rx;


#define EX_UART_NUM UART_NUM_1
#define BUF_SIZE (1024)
#define RD_BUF_SIZE (BUF_SIZE)
static QueueHandle_t uart0_queue;
uint8_t recieve_cmd[][2] = {
    {0xa3,0x0d}
};
uint8_t send_data[8];

static void uart_event_task(void *pvParameters)
{
    uart_event_t event;
    uint8_t* dtmp = (uint8_t*) malloc(RD_BUF_SIZE);
    for(;;) {
        //Waiting for UART event.
        if(xQueueReceive(uart0_queue, (void * )&event, (portTickType)portMAX_DELAY)) {
            bzero(dtmp, RD_BUF_SIZE);
            // ESP_LOGI(TAG, "uart[%d] event:", EX_UART_NUM);
            switch(event.type) {
                //Event of UART receving data
                /*We'd better handler data event fast, there would be much more data events than
                other types of events. If we take too much time on data event, the queue might
                be full.*/
                case UART_DATA:
                    // ESP_LOGI(TAG, "[UART DATA]: %d", event.size);
                    uart_read_bytes(EX_UART_NUM, dtmp, event.size, portMAX_DELAY);   
                    if (memcmp(recieve_cmd[0],  dtmp, sizeof(recieve_cmd[0])) == 0) {
                        // printf("Arrays are equal\n");
                        int64_t uart_dev_time = esp_timer_get_time();
                        memcpy(send_data, &uart_dev_time, sizeof(int64_t));
                        uart_write_bytes(EX_UART_NUM, (const char*) send_data, 8);
                        ESP_LOGI(TAG, "[UART Time]: %lld", uart_dev_time);
                        // uart_dev_send(uart_dev_time,8);
                        // uart_dev_delete_buffer();
                    } 
                    break;
                //Event of HW FIFO overflow detected
                case UART_FIFO_OVF:
                    ESP_LOGI(TAG, "hw fifo overflow");
                    // If fifo overflow happened, you should consider adding flow control for your application.
                    // The ISR has already reset the rx FIFO,
                    // As an example, we directly flush the rx buffer here in order to read more data.
                    uart_flush_input(EX_UART_NUM);
                    xQueueReset(uart0_queue);
                    break;
                //Event of UART ring buffer full
                case UART_BUFFER_FULL:
                    ESP_LOGI(TAG, "ring buffer full");
                    // If buffer full happened, you should consider encreasing your buffer size
                    // As an example, we directly flush the rx buffer here in order to read more data.
                    uart_flush_input(EX_UART_NUM);
                    xQueueReset(uart0_queue);
                    break;
                //Event of UART RX break detected
                case UART_BREAK:
                    ESP_LOGI(TAG, "uart rx break");
                    break;
                //Event of UART parity check error
                case UART_PARITY_ERR:
                    ESP_LOGI(TAG, "uart parity error");
                    break;
                //Event of UART frame error
                case UART_FRAME_ERR:
                    ESP_LOGI(TAG, "uart frame error");
                    break;
                //UART_PATTERN_DET
                case UART_PATTERN_DET:
                    break;
                //Others
                default:
                    ESP_LOGI(TAG, "uart event type: %d", event.type);
                    break;
            }
        }
    }
    free(dtmp);
    dtmp = NULL;
    vTaskDelete(NULL);
}

void uart_dev_init(void) {
   esp_log_level_set(TAG, ESP_LOG_INFO);
   const uart_config_t uart_config = {
      .baud_rate = 115200,//19200,
      .data_bits = UART_DATA_8_BITS,
      .parity = UART_PARITY_DISABLE,
      .stop_bits = UART_STOP_BITS_1,
      .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
      .source_clk = UART_SCLK_APB,
   };
   // We won't use a buffer for sending data.
   uart_driver_install(EX_UART_NUM, BUF_SIZE * 2, BUF_SIZE * 2, 20, &uart0_queue, 0);
   uart_param_config(EX_UART_NUM, &uart_config);
   

   //Set UART log level
   esp_log_level_set(TAG, ESP_LOG_INFO);
   //Set UART pins
   uart_set_pin(EX_UART_NUM, TXD_PIN, RXD_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
   
   s_uart_steam_rx = xStreamBufferCreate(1024 * 4 , 1);
   if (!s_uart_steam_rx) {
      ESP_LOGE(TAG, "%s, init fail, the gatts StreamBuffer create fail.", __func__);
      return;
   }
   //Create a task to handler UART event from ISR
   xTaskCreate(uart_event_task, "uart_event_task", 1024*4, NULL, 12, NULL);   
}
/**
 * @brief 串口接收函数
 * 
 * @param buf 存储指针
 * @param len 读取长度(-1为不设置固定读取长度)
 * @param timeout_ms 超时时间
 * @return uint16_t 
 */
uint16_t uart_dev_recive(void *buf,int len, uint32_t timeout_ms){
   
    uint16_t buf_len = xStreamBufferReceive(s_uart_steam_rx,buf,len,pdMS_TO_TICKS(timeout_ms));
    if((buf_len!=len)&&(len!=-1)){
        ESP_LOGE(TAG,"buf_len:%d    buf_len!=len",buf_len);
    }
    // ESP_LOG_BUFFER_HEX("uart_rx",buf,buf_len);
   return buf_len;
}

void uart_dev_send(const void *buf,uint16_t len){
   uart_write_bytes(EX_UART_NUM, (const char*) buf, len);
}