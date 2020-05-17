#!/usr/bin/env python
"""
Sending SMS using AT Commands
"""
from optparse import OptionParser
import serial
import time
import sys

device = '/dev/ttyS0'

class smsmodem:

    def __init__(self):
        self.regstatus = 0
        self.registered = False
        # rssi (received signal strength), ber (bit error rate)
        self.rssi = ''
        self.ber = ''
        self.device = serial.Serial(device, 115200, timeout=1)
        if not self.device.isOpen():
            raise NameError, 'comm port error'

    def reset(self):
        """reset to factory defaults"""
        if not (self.sendcmd('at&f\r\n')):
            raise NameError, 'something bad happened'
        # set to text mode
        if not self.sendcmd('at+cmgf=1\r\n'):
            raise NameError, 'failed to set text mode'

    # function for sending
    @staticmethod
    def sendmsg(sender, message):
        serialport = serial.Serial(device,115200, timeout=1)
        serialport.write('AT+CMGF=1\r')
        time.sleep(1)
        serialport.write('AT+CMGS="'+sender+'"\r\n')
        time.sleep(1)
        serialport.write(message + "\x1A")
        time.sleep(1)
        return True

    def checkSignal(self):
        """ 10-31 = sufficient
            0-9   = weak or insufficient
            99    = insufficient"""
        # rssi (received signal strength), ber (bit error rate)
        self.rssi, self.ber = self.sendcmd("at+csq\r\n").split()[1].split(',')  # rssi
        # print self.signal
        if self.rssi == 99:
            return False
        else:
            return True

    def sendcmd(self, cmd):
        """send a command to the modem and get its response
        note: does not automatically append \n or \r characters"""
        self.device.write(cmd)
        response = self.device.readlines()[1].strip()
        # print response
        return response

    def isRegistered(self):
        """0: not registered
        1: registered to home network
        2: not registered, but searching
        3: registration denied
        4: unknown (not used)
        5: registered, roaming"""
        self.regstatus = self.sendcmd("at+creg?\r\n")[-1]  # last character
        if self.regstatus == '1' or self.regstatus == '5':
            self.registered = True  # not sure what to do when it's searching
            return True
        else:
            return False

# x = raw_input("type the number: \n")
# y = raw_input("type the message: \n")

def num_only(num):
    """return numbers only"""
    newnum = []
    for c in num:
        if c.isdigit():
            newnum.append(c)
    return ''.join(newnum)

def main():
    # parser stuff
    parser = OptionParser()
    parser.add_option("-n", "--number", type="string", dest="number", help="10-digit phone number(s), comma separated")
    parser.add_option("-t", "--txt", type="string", dest="txt", help="txt message body")
    parser.add_option("-R", "--registration-check", action="store_true", dest='regchk',
                      help="check network registration status", default="False")
    parser.add_option("-S", "--signal-check", action="store_true", dest='sigchk',
                      help="check signal strength and bit error rate", default="False")

    (options, args) = parser.parse_args()
    # sanity checking
    if len(sys.argv) > 1 and not args:
        if (options.txt or options.number) and not (options.txt and options.number):
            parser.error("-n and -t are both required options.")
        elif options.txt and options.number:
            if options.regchk == True or options.sigchk == True:
                parser.error("please send message and check the modem separately.")
            else:
                numbers = options.number.split(',')
                # first loop for sanity checking
                for i, number in enumerate(numbers):
                    number = num_only(number)
                    numbers[i] = number
                    if len(number) != 10:
                        parser.error("%s, 10-digit phone numbers only." % number)
                # second loop to send message
                sms = smsmodem()
                # sms.reset()
                for number in numbers:
                    if sms.sendmsg(number, options.txt):
                        print "message to %s sent successfully" % number
        else:
            sms = smsmodem()
            # sms.reset()
            if options.sigchk:
                sms.checkSignal()
                print "rssi: %s, ber: %s" % (sms.rssi, sms.ber)
            if options.regchk:
                if sms.isRegistered():
                    print "modem registration (%s) successful" % sms.regstatus
                else:
                    print "modem registration (%s) failed" % sms.regstatus

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
