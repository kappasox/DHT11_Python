#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# DHT11 Class Library with pigpio
#
# This class is a refactoring of a library 
# originally written by Zoltan Szarvas using RPi.GPIO,
# converted to use the pigpio library.
#
# Aug. 19, 2025
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

import time
import pigpio

class DHT11MissingDataError(Exception): 
    pass

class DHT11CRCError(Exception): 
    pass

class DHT11:
    'DHT11 sensor reader class for Raspberry Pi using pigpio'

    def __init__(self, pin):
        self.__pin = pin
        self.__pi = pigpio.pi()
        if not self.__pi.connected:
            raise RuntimeError('pigpio daemon not running!')

    def read(self):
        # DHT11プロトコルに従いピン制御
        self.__pi.set_mode(self.__pin, pigpio.OUTPUT)
        self.__pi.write(self.__pin, 1)
        time.sleep(0.58)
        self.__pi.write(self.__pin, 0)
        time.sleep(0.02)
        self.__pi.set_mode(self.__pin, pigpio.INPUT)
        self.__pi.set_pull_up_down(self.__pin, pigpio.PUD_UP)

        # データ収集
        data = self.__collect_input()
        # データ解析
        pull_up_lengths = self.__parse_data_pull_up_lengths(data)
        if len(pull_up_lengths) != 40:
            raise DHT11MissingDataError
        bits = self.__calculate_bits(pull_up_lengths)
        the_bytes = self.__bits_to_bytes(bits)
        checksum = self.__calculate_checksum(the_bytes)
        if the_bytes[4] != checksum:
            raise DHT11CRCError
        temperature = the_bytes[2] + float(the_bytes[3]) / 10
        humidity = the_bytes[0] + float(the_bytes[1]) / 10
        return temperature, humidity, checksum

    def __collect_input(self):
        unchanged_count = 0
        max_unchanged_count = 100
        last = -1
        data = []
        start = time.time()
        while True:
            current = self.__pi.read(self.__pin)
            data.append(current)
            if last != current:
                unchanged_count = 0
                last = current
            else:
                unchanged_count += 1
                if unchanged_count > max_unchanged_count:
                    break
            if time.time() - start > 0.1:
                break
        return data

    def __parse_data_pull_up_lengths(self, data):
        STATE_INIT_PULL_DOWN = 1
        STATE_INIT_PULL_UP = 2
        STATE_DATA_FIRST_PULL_DOWN = 3
        STATE_DATA_PULL_UP = 4
        STATE_DATA_PULL_DOWN = 5

        state = STATE_INIT_PULL_DOWN
        lengths = []
        current_length = 0
        for i in range(len(data)):
            current = data[i]
            current_length += 1
            if state == STATE_INIT_PULL_DOWN:
                if current == 0:
                    state = STATE_INIT_PULL_UP
                    continue
                else:
                    continue
            if state == STATE_INIT_PULL_UP:
                if current == 1:
                    state = STATE_DATA_FIRST_PULL_DOWN
                    continue
                else:
                    continue
            if state == STATE_DATA_FIRST_PULL_DOWN:
                if current == 0:
                    state = STATE_DATA_PULL_UP
                    continue
                else:
                    continue
            if state == STATE_DATA_PULL_UP:
                if current == 1:
                    current_length = 0
                    state = STATE_DATA_PULL_DOWN
                    continue
                else:
                    continue
            if state == STATE_DATA_PULL_DOWN:
                if current == 0:
                    lengths.append(current_length)
                    state = STATE_DATA_PULL_UP
                    continue
                else:
                    continue
        return lengths

    def __calculate_bits(self, pull_up_lengths):
        shortest_pull_up = 1000
        longest_pull_up = 0
        for i in range(0, len(pull_up_lengths)):
            length = pull_up_lengths[i]
            if length < shortest_pull_up:
                shortest_pull_up = length
            if length > longest_pull_up:
                longest_pull_up = length
        halfway = shortest_pull_up + (longest_pull_up - shortest_pull_up) / 2
        bits = []
        for i in range(0, len(pull_up_lengths)):
            bit = False
            if pull_up_lengths[i] > halfway:
                bit = True
            bits.append(bit)
        return bits

    def __bits_to_bytes(self, bit_list0):
        bytes = []
        length = len(bit_list0)
        byte_d = 0
        for i in range(0, length):
            byte_d = byte_d << 1
            if (1 == bit_list0[i]):
                byte_d = byte_d | 1
            else:
                byte_d = byte_d | 0
            if ((i + 1) % 8 == 0):
                bytes.append(byte_d)
                byte_d = 0
        return bytes

    def __calculate_checksum(self, bytes0):
        checksum = (bytes0[0] & 0xff) + (bytes0[1] & 0xff) + (bytes0[2]  & 0xff) + (bytes0[3] & 0xff)
        return checksum

    def close(self):
        self.__pi.stop()

if __name__ == '__main__':
    import datetime
    dht11_instance = DHT11(pin=26)
    print("DHT11 sensor initialized on pin 26.")
    try:
        while True:
            try:
                tempe, hum, check = dht11_instance.read()
                print("Last valid input: " + str(datetime.datetime.now()))
                print("Temperature: %-3.1f C" % tempe)
                print("Humidity: %-3.1f %%" % hum)
            except DHT11CRCError:
                print('DHT11CRCError: ' + str(datetime.datetime.now()))
            except DHT11MissingDataError:
                print('DHT11MissingDataError: '+ str(datetime.datetime.now()))
            time.sleep(3)
    except KeyboardInterrupt:
        print('Ctrl-C is pressed.')
        print('Closing DHT11 instance.')
        dht11_instance.close()
