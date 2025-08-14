# DHT11_Python

DHT11 Class Library with lgpio (for lecture)

DHT11 Class Library for Python over Raspberry Pi OS

Modification of Zoltan Szarvas's library with RPI.GPIO.
https://github.com/szazo/DHT11_Python.git

This code has been refactored for a lecture,
converting the original RPi.GPIO library into a class using lgpio.

# Environment

We have checked this class library for Python 3.11.2 and venv over Raspberry Pi OS (Bookworm, 64-bit) on Raspberry Pi 4B.

# Note
Since we are using Raspberry Pi OS (a non-real-time OS) and Python (an interpreter), we cannot guarantee timing. This is a poor combination for the clockless DHT11 sensor. However, this setup is perfect for a lecture on OS behavior, as the chance of a sensor error changes with the number of running processes. (Michiharu Takemoto)