#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/uart.h"
#include "esp_log.h"

// #include "uart_dev.h"
#include "as5600_app.h"
static const char *TAG = "main";

void app_main(void)
{
    as5600_app_init();
    while (1){
    // ESP_LOGI("MAIN","bat:----------------%d%%----------------- ischarge:%d GPIO[%d]:%d",pwr_user_get_bat_percent(),pwr_user_is_charge(),PWR_CHARG_PIN,gpio_get_level(PWR_CHARG_PIN));
    vTaskDelay(10 / portTICK_PERIOD_MS);
    }
}
