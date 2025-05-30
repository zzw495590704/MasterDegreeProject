Project: 
    as5600_driver
Brief: 
    As5600 double channel for ESP32S3
====================================
IO config：
IIC0: SDA0 --> 6 | SCL0 --> 5
IIC1: SDA1 --> 9 | SCL1 --> 10
====================================

File:
    as5600_dev: as5600 device driver, include inited device and read raw data of as5600.
    as5600_app: as5600 device application, processing data from as5600_dev. 