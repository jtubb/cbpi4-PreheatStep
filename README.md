# CBPi4 I2C Analog Input

## I2C Analog Sensor Plugin for CBPi4 ADS1x15

## Installation/Upgrade

From your command line run the following:

```
sudo pip3 install --upgrade https://github.com/jtubb/cbpi4-ads1x15/archive/main.zip
```

Requires cbpi>=4.0.0.45, current development branch.

## Settings

Settings will be added by this plugin:
- Chip: ADS1015 (12 bit resolution) or ADS1115 (16 bit resolution)
- Address: Address of the ADS1x15 device. Boards can be set to one of the following '0x48', '0x49', '0x4a', '0x4b' using hardware jumpers (see datasheet).If no devices are listed ensure you have enabled I2C on your Raspberry PI and check if the device exists in ("/dev/i2c-*")
- Channel (0-3): Input channel to read from.
- Gain: Programmable gain for the chip.

GAIN    RANGE (V)
----    ---------
2/3    +/- 6.144
  1    +/- 4.096
  2    +/- 2.048
  4    +/- 1.024
  8    +/- 0.512
 16    +/- 0.256

- Min_Range - Sensor value to map to 0% output of the sensor.
- Max_Range - Sensor value to map to 100% output of the sensor.
- Read_Mode - Output Raw Value or Range from 0-100

## Use as a 4-20mA input

##  Changelog

**11.23.22: Initial release
