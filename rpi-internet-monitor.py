#!/usr/bin/env python

import subprocess
import sys
import time
import logging
import pexpect

THIS_IS_ON_RPI = False
try:
    import RPi.GPIO as GPIO
    THIS_IS_ON_RPI = True
except:
    pass

GPIO_SHUTDOWN_SWITCH = 24  # switch for shutdown
GPIO_SHUTDOWN_LED = 23     # led for indicating raspberry pi connected
GPIO_GREEN_LIGHT = 17      # led for internet working
GPIO_AMBER_LIGHT = 27      # led for internet marginally working
GPIO_RED_LIGHT = 22        # led for internet is not working

TIMES_TO_PING_NODE = 3     # ping each node this many times
DELAY_BETWEEN_PINGS = 0.3    # delay in seconds
DELAY_BETWEEN_TESTS = 1    # delay in seconds

SITES = ["google.com", "comcast.com", "yahoo.com", "twc.com", "bing.com", "facebook.com"]

"""      replaced with logging module
# print messages for debugging when indicator is set
def debug_message(debug_indicator, output_message):
    if debug_indicator:
        print output_message
"""

# issue Linux ping command to determine internet connection status
def ping(site):
    child = pexpect.spawn('ping -c ' + str(TIMES_TO_PING_NODE) + ' ' + site)
    output = []
    while True:
        line = child.readline()
        if not line: 
            break
        output.append(line)
    if len(output) >= 2:
        last_line = output.pop()
        next_line = output.pop()
        parts = next_line.split('%')
        packet_loss = int(parts[0][-1])
    else:
        packet_loss = 100
        last_line = 'no round trip times available'
    print '{} site packetloss = {}% {}'.format(site, packet_loss, last_line)
    #print last_line
    # return loss percentage
    return packet_loss

    """
    cmd = "/bin/ping -c 1 " + site
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError, e:
        debug_message(debug, site + ": not reachable")
        return 0
    else:
        debug_message(debug, site + ": reachable")
        return 1
    """


# ping the sites in the site list the specified number of times
# and calculate the percentage of successful pings
def ping_sites(site_list, wait_time, times):
    #successful_pings = 0
    packet_loss_list = []
    attempted_pings = times * len(site_list)
    for test in range(0, times):
        for site in site_list:
            #successful_pings += ping(s)
            packet_loss_list.append(ping(site))
            time.sleep(wait_time)
    #debug_message(debug, "Percentage successful: " + str(int(100 * (successful_pings / float(attempted_pings)))) + "%")
    #return successful_pings / float(attempted_pings)   # return percentage successful 
    # calculate avg percentage of packet loss
    total_loss = 0
    for plr in packet_loss_list:
        total_loss += plr
    avg_loss = total_loss / float(len(packet_loss_list))
    #return packet_loss / float(attempted_pings)
    return avg_loss

# turn the amber lamp on   
def lamp_amber_on():
    if THIS_IS_ON_RPI:
        #debug_message(debug, ">>> Turn Red OFF; Turn Amber ON; Turn Green OFF")
        GPIO.output(GPIO_RED_LIGHT, False)
        GPIO.output(GPIO_AMBER_LIGHT, True)
        GPIO.output(GPIO_GREEN_LIGHT, False)

# turn the green lamp on
def lamp_green_on():
    if THIS_IS_ON_RPI:
        #debug_message(debug, ">>> Turn Red OFF; Turn Amber OFF; Turn Green ON")
        GPIO.output(GPIO_RED_LIGHT, False)
        GPIO.output(GPIO_AMBER_LIGHT, False)
        GPIO.output(GPIO_GREEN_LIGHT, True)

# turn the red lamp on
def lamp_red_on():
    if THIS_IS_ON_RPI:
        #debug_message(debug, ">>> Turn Red ON; Turn Amber OFF; Turn Green OFF")
        GPIO.output(GPIO_RED_LIGHT, True)
        GPIO.output(GPIO_AMBER_LIGHT, False)
        GPIO.output(GPIO_GREEN_LIGHT, False)

# turn all of the lamps off
def lamp_all_off():
    if THIS_IS_ON_RPI:
        #debug_message(debug, ">>> Turn Red OFF; Turn Amber OFF; Turn Green OFF")
        GPIO.output(GPIO_RED_LIGHT, False)
        GPIO.output(GPIO_AMBER_LIGHT, False)
        GPIO.output(GPIO_GREEN_LIGHT, False)

# flash all of the lamps in sequence five times
def lamp_test():
    #debug_message(debug, "Testing Lights")
    TEST_DELAY = 0.1           # tenth of a second delay   
    for i in range(0, 5):
        time.sleep(TEST_DELAY)
        lamp_red_on()
        time.sleep(TEST_DELAY)
        lamp_amber_on()
        time.sleep(TEST_DELAY)
        lamp_green_on()
    lamp_all_off()
    #debug_message(debug, "Light test completed")
            
# main program starts here

# check to see if the user wants to print debugging messages
debug = False
if len(sys.argv) > 1:
    if sys.argv[1] == "-debug":
        debug = True
    else:
        print "unknown option specified: " + sys.argv[1]
        sys.exit(1)

if THIS_IS_ON_RPI:
    # setup the GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_GREEN_LIGHT, GPIO.OUT)
    GPIO.setup(GPIO_AMBER_LIGHT, GPIO.OUT)
    GPIO.setup(GPIO_RED_LIGHT, GPIO.OUT)

# flash the lamps to indicate the program is starting
lamp_all_off()
lamp_test()
time.sleep(0.5)
lamp_amber_on()     # turn amber lamp on during the first test

# main loop: ping sites, turn appropriate lamp on, wait, repeat
test = 0
while True:
    test+=1
    #debug_message(debug, "----- Test " + str(test) + " -----")
    success = ping_sites(SITES, DELAY_BETWEEN_PINGS, TIMES_TO_PING_NODE)
    print 'packet loss = {}%'.format(success)
    if success > .75:
        print 'Internet not responding'
        lamp_red_on()
    elif success > .25:  
        print 'Internet slow'
        lamp_amber_on()
    else:
        print 'Internet ALL good'
        lamp_green_on()
    #debug_message(debug, "Waiting " + str(DELAY_BETWEEN_TESTS) + " seconds until next test.")
    time.sleep(DELAY_BETWEEN_TESTS)
    print

