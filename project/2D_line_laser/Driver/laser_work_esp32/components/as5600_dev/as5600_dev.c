#include "as5600_dev.h"

static const char *TAG = "as5600_dev";
#define I2C_MASTER_FREQ_HZ          400000                     /*!< I2C master clock frequency */
#define I2C_MASTER_TX_BUF_DISABLE   0                          /*!< I2C master doesn't need buffer */
#define I2C_MASTER_RX_BUF_DISABLE   0                          /*!< I2C master doesn't need buffer */
#define I2C_MASTER_TIMEOUT_MS       1000

#define AS600_SENSOR_ADDR           0x36    

#define I2C_MASTER_SCL0_IO           (GPIO_NUM_5)      /*!< GPIO number used for I2C master clock */
#define I2C_MASTER_SDA0_IO           (GPIO_NUM_6)      /*!< GPIO number used for I2C master data  */
#define I2C_MASTER_NUM0              0                          /*!< I2C master i2c port number, the number of i2c peripheral interfaces available will depend on the chip */
#define I2C_MASTER_SCL1_IO           (GPIO_NUM_9)      /*!< GPIO number used for I2C master clock */
#define I2C_MASTER_SDA1_IO           (GPIO_NUM_10)      /*!< GPIO number used for I2C master data  */
#define I2C_MASTER_NUM1              1                          /*!< I2C master i2c port number, the number of i2c peripheral interfaces available will depend on the chip */


#define AS600_SENSOR_ADDR                 0x36        
#define AS5600_ANGLE_H           0x0e      
#define AS5600_ANGLE_L           0x0f
#define AS5600_MAX_VALUE         4096

static as5600_dev as5600_dev0={
    .i2c_port = I2C_MASTER_NUM0,
    .SCL_IO = I2C_MASTER_SCL0_IO,
    .SDA_IO = I2C_MASTER_SDA0_IO
};
static as5600_dev as5600_dev1={
    .i2c_port = I2C_MASTER_NUM1,
    .SCL_IO = I2C_MASTER_SCL1_IO,
    .SDA_IO = I2C_MASTER_SDA1_IO
};


static esp_err_t as5600_dev_read(i2c_port_t i2c_master_port, uint8_t reg_addr, uint8_t *data, size_t len)
{
    return i2c_master_write_read_device(i2c_master_port, AS600_SENSOR_ADDR, &reg_addr, 1, data, len, I2C_MASTER_TIMEOUT_MS / portTICK_RATE_MS);
}

uint16_t as5600_dev_get_value(i2c_port_t i2c_master_port){
    uint16_t result = 0;
    uint8_t data[2];
    as5600_dev_read(i2c_master_port,AS5600_ANGLE_H, &data[0], 1);
    as5600_dev_read(i2c_master_port,AS5600_ANGLE_L, &data[1], 1);
    // ESP_LOG_BUFFER_HEX(TAG,data,2);
    result=(uint16_t)(data[0]<<8|data[1]); //一共就11位 注意
    return result;
}

static esp_err_t as5600_dev_iic_init(as5600_dev dev){
    int i2c_master_port = dev.i2c_port;
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = dev.SDA_IO,
        .scl_io_num = dev.SCL_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };

    i2c_param_config(i2c_master_port, &conf);

    return i2c_driver_install(i2c_master_port, conf.mode, I2C_MASTER_RX_BUF_DISABLE, I2C_MASTER_TX_BUF_DISABLE, 0);
}
uint16_t as5600_dev_iic0_read(){
    return as5600_dev_get_value(I2C_MASTER_NUM0);
}
uint16_t as5600_dev_iic1_read(){
    return as5600_dev_get_value(I2C_MASTER_NUM1);
}
void as5600_dev_init(){
    //device init
    ESP_ERROR_CHECK(as5600_dev_iic_init(as5600_dev0));
    ESP_ERROR_CHECK(as5600_dev_iic_init(as5600_dev1));
    ESP_LOGI(TAG,"as5600 dev inited");
    ESP_LOGI(TAG,"I2C[%d]: SCL->%d SDA->%d || I2C[%d]: SCL->%d SDA->%d ",
        as5600_dev0.i2c_port,as5600_dev0.SCL_IO,as5600_dev0.SDA_IO,
        as5600_dev1.i2c_port,as5600_dev1.SCL_IO,as5600_dev1.SDA_IO);
}