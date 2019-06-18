# Install dependencies
sudo apt-get install python3-pil python3-pip
sudo pip3 install adafruit-blinka adafruit-circuitpython-ssd1306

# Enable I2C
sudo raspi-config nonint do_i2c 0
