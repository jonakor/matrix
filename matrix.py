#!/usr/bin/env python3

import time
from neopixel import *
import argparse
import bluetooth
import threading
import numpy as np
import random
import matrix_text as text

MATRIX_ROW = 5
MATRIX_COL = 10
NUM_LEDS = MATRIX_ROW*MATRIX_COL
MATRIX_FPS = 30
SLEEP = 1.0/MATRIX_FPS
# LED strip configuration:
LED_COUNT      = NUM_LEDS      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

## BOOT color
red = 0
green = 0
blue = 255

# GLOBAL VARs
brightness = LED_BRIGHTNESS
strip = 0
frequency = 1.0

server_socket = 0
client_socket = 0

sinusFlag = False
pulseFlag = False
randomizerFlag = False
textFlag = False

inText = 'HELLO!'

# Define functions which animate LEDs in various ways.
def initApp():
    global frequency, strip, brightness
    initTime = time.time()
    while pulseFlag:
        tid = time.time()
        rad = 2*np.pi*tid*frequency
        base = 20
        amplitude = (brightness-base)/2
        offset = amplitude + base
        strip.setBrightness(int(amplitude*np.sin(rad) + offset))
        for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(int(red), int(green), int(blue)))
        strip.show()
        time.sleep(SLEEP)

        if (time.time() - initTime) > 20:
            break

    brightness = 50
    frequency = 0.2

    sinusApp()
    frequency = 1.0
    brightness = LED_BRIGHTNESS


def colorWipe(strip, color):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)


def setupLED():
    global strip
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()


def setupComm():
    global server_socket
    global client_socket
    server_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM)
    print("Waiting for connection...")

    port = 1
    server_socket.bind(("",port))
    server_socket.listen(1)
    client_socket,address = server_socket.accept()
    print('Accepted connection from ',address)
    print('Bluetooth Connected!')


def readBluetooth():
    global red, green, blue, strip, sinusFlag, pulseFlag, randomizerFlag, textFlag, frequency, brightness, inText
    while True:
        data = client_socket.recv(1024)
        search = "SE"
        flag = 0
        for i in range(2):
            if (data.find(search[i]) < 0):
                flag = 1
        if flag == 1:
            continue

        data = data[data.find('S')+1:data.find('E')]
        #print data
        if (data[0] == '1'):
            pulseFlag = False
            sinusFlag = False
            randomizerFlag = False
            textFlag = False
            red = int(data[data.find('R')+1:data.find('G')-1])
            green = int(data[data.find('G')+1:data.find('B')-1])
            blue = int(data[data.find('B')+1:])

        elif (data[0] == '2'):
            red = int(data[data.find('R')+1:data.find('G')-1])
            green = int(data[data.find('G')+1:data.find('B')-1])
            blue = int(data[data.find('B')+1:])
        elif (data[0] == '3'):
            brightness = int(255*float(data[1:])/100)
            strip.setBrightness(int(brightness))

        elif (data[0] == '4'):
            frequency = float(data[1:])/1000.0

        elif (data[0] == '5'):
            pulseFlag = False
            sinusFlag = False
            textFlag = False
            randomizerFlag = not randomizerFlag

        elif (data[0] == '6'):
            pulseFlag = False
            randomizerFlag = False
            textFlag = False
            sinusFlag = not sinusFlag

        elif (data[0] == '7'):
            sinusFlag = False
            randomizerFlag = False
            textFlag = False
            pulseFlag = not pulseFlag

        elif (data[0] == '9'):
            sinusFlag = False
            randomizerFlag = False
            pulseFlag = False
            textFlag = not textFlag

            inText = data[1:]
	    print inText

        time.sleep(SLEEP)


def appHandler():
   while True:
        sinusApp()
        pulseApp()
        randomizer()
	displayText()
        if (not sinusFlag) and (not pulseFlag) and (not randomizerFlag) and (not textFlag):
            defaultApp()


def sinusApp():
    global strip
    divisor = 2*MATRIX_COL
    topi = 2*np.pi
    base = 20
    amplitude = (255-base)/2
    offset = base + amplitude
    while sinusFlag:
        tid = time.time()
        rad = topi*tid*frequency
        for i in range(MATRIX_COL):

            red = amplitude*np.sin(rad + i*topi/divisor) + offset
            green = amplitude*np.sin(rad + i*topi/divisor + topi/3) + offset
            blue = amplitude*np.sin(rad + i*topi/divisor + 2*topi/3) + offset
            for j in range(MATRIX_ROW):
                strip.setPixelColor(j*10 + i, Color(int(red), int(green), int(blue)))

        strip.setBrightness(int(brightness))
        strip.show()
        time.sleep(SLEEP)

def defaultApp():
    global strip
    for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(int(red), int(green), int(blue)))
    strip.setBrightness(int(brightness))
    strip.show()
    time.sleep(SLEEP)

def pulseApp():
    global strip

    while pulseFlag:
        tid = time.time()
        rad = 2*np.pi*tid*frequency
        base = 20
        amplitude = (brightness-base)/2
        offset = amplitude + base
        strip.setBrightness(int(amplitude*np.sin(rad) + offset))
        for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(int(red), int(green), int(blue)))
        strip.show()
        time.sleep(SLEEP)

def displayText():
    global strip, intext, textFlag
    roll = text.text_to_roll(inText)
    index = 0
    image = [[40,41,42,43,44,45,46,47,48,49],[30,31,32,33,34,35,36,37,38,39],[20,21,22,23,24,25,26,27,28,29],[10,11,12,13,14,15,16,17,18,19],[0,1,2,3,4,5,6,7,8,9]]


    while textFlag:
	print('intext')
        done = True
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(int(red), int(green), int(blue)))
        for i in range(5):
            for j in range(10):
                if roll[i][index+j] == 1:
                    done = False
                    strip.setPixelColor(image[i][j], Color(int(blue), int(red), int(green)))
	strip.show()
	time.sleep(0.5)
        if done:
            index = 0



def randomizer():
    global strip

    if not randomizerFlag:
        return

    frame = [0,1,2,3,4,5,6,7,8,9,19,29,39,49,48,47,46,45,44,43,42,41,40,30,20,10]

    colorWipe(strip, Color(int(red), int(green), int(blue)))
    strip.setPixelColor(25, Color(int(green), int(blue), int(red)))
    strip.show()
    time.sleep(1)

    colorWipe(strip, Color(int(red), int(green), int(blue)))
    strip.setPixelColor(15, Color(int(green), int(blue), int(red)))
    strip.setPixelColor(35, Color(int(green), int(blue), int(red)))
    strip.show()
    time.sleep(1)

    colorWipe(strip, Color(int(red), int(green), int(blue)))
    strip.setPixelColor(5, Color(int(green), int(blue), int(red)))
    strip.setPixelColor(45, Color(int(green), int(blue), int(red)))
    strip.show()
    time.sleep(0.1)

    player1 = 5
    player2 = 17
    prev1 = player1
    prev2 = player2

    target1 = random.randint(150,250)
    target2 = random.randint(150,250)

    speed1 = random.randint(1,5)
    speed2 = random.randint(1,5)
    wait1 = speed1
    wait2 = speed2

    while randomizerFlag:
        wait1 -= 1
        wait2 -= 1

        if wait1 < 1 and target1 > 0:
            player1 += 1
            target1 -= 1
            if player1 == 26:
                player1 = 0
            if target1 < 50 and speed1 < 100:
                speed1 += 1
            wait1 = speed1

        if wait2 < 1 and target2 > 0:
            player2 += 1
            target2 -= 1
            if player2 == 26:
                player2 = 0
            if target2 < 50 and speed2 < 100:
                speed2 += 1
            wait2 = speed2

        if prev1 != player1 or prev2 != player2:
            colorWipe(strip, Color(int(red), int(green), int(blue)))
            if prev1 != player1:
                prev1 = player1
            if prev2 != player2:
                prev2 = player2

            strip.setPixelColor(frame[player1], Color(int(green), int(blue), int(red)))
            strip.setPixelColor(frame[player2], Color(int(green), int(blue), int(red)))
            strip.setBrightness(int(brightness))
            strip.show()

        if (target1 == 0) and (target2 == 0):
            break

        time.sleep(0.01)

    for i in range(5):
        colorWipe(strip, Color(int(red), int(green), int(blue)))
        strip.setPixelColor(frame[player1], Color(int(green), int(blue), int(red)))
        strip.setPixelColor(frame[player2], Color(int(green), int(blue), int(red)))
        strip.show()
        time.sleep(0.5)

        colorWipe(strip, Color(int(red), int(green), int(blue)))
        strip.show()
        time.sleep(0.5)


try:
    setupLED()

    pulseFlag = True
    sinusFlag = True
    initThread = threading.Thread(target = initApp)
    initThread.daemon = True
    initThread.start()

    setupComm()
    pulseFlag = False
    sinusFlag = False

    initThread.join()

    red = 0
    green = 255
    blue = 0
    colorWipe(strip, Color(int(red), int(green), int(blue)))
    strip.show()
    time.sleep(2)
    red = 0
    green = 50
    blue = 200

    btThread = threading.Thread(target = readBluetooth)
    btThread.daemon = True
    btThread.start()

    appThread = threading.Thread(target = appHandler)
    appThread.daemon = True
    appThread.start()

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print('Exiting the Matrix..')
    colorWipe(strip, Color(0,0,0))
    strip.show()
    print('Bye')
