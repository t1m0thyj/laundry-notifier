# Install GPIO Zero
sudo apt-get -y install python3-gpiozero

# Install PiOLED dependencies
sudo apt-get -y install python3-pil python3-smbus
git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
cd Adafruit_Python_SSD1306
sudo python3 setup.py install

# Enable SPI and I2C
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
