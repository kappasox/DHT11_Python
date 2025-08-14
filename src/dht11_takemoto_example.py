#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# How to use DHT11 Class Library with lgpio
#
# using lgpio
# To install lgpio,
# $ pip install lgpio # with venv. Recommended
# or
# $ sudo apt-get install python3-lgpio # not recommended
# .
#
# Aug. 14, 2025
# Michiharu Takemoto (takemoto.development@gmail.com)
#
#
# MIT License
# 
# Copyright (c) 2025 Michiharu Takemoto <takemoto.development@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 

import dht11_takemoto as dht11
import time
import datetime


if __name__ == '__main__':
    # read data using pin 26
    dht11_instance = dht11.DHT11(pin=26)
    print("DHT11 sensor initialized on pin 26.")

    try:
         while True:
            try:
                tempe, hum, check = dht11_instance.read()
                print("Last valid input: " + str(datetime.datetime.now()))
                print("Temperature: %-3.1f C" % tempe)
                print("Humidity: %-3.1f %%" % hum)
            except dht11.DHT11CRCError:
                print('DHT11CRCError: ' + str(datetime.datetime.now()))
            except dht11.DHT11MissingDataError:
                print('DHT11MissingDataError: '+ str(datetime.datetime.now()))
			
            time.sleep(3)

    except KeyboardInterrupt:
        print('Ctrl-C is pressed.')
        print('Closing DHT11 instance.')
        dht11_instance.close()
