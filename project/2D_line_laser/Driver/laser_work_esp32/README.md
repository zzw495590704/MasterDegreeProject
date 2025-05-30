Project: 
    laser_work
Brief: 
    as5600 read velocity of A-axis, output PWM to Laser.
====================================
IO config：
IIC0: SDA0 --> 6 | SCL0 --> 5
PWM:  9
====================================

File:
    as5600_dev: as5600 device driver, include inited device and read raw data of as5600.
    as5600_app: as5600 device application, processing data from as5600_dev. 