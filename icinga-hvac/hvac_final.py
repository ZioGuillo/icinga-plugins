#!/usr/bin/env python3
# Import variables from the system
import sys
from optparse import OptionParser, OptionGroup
from requests_html import HTMLSession

# Nagios return codes
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

usage = "Usage: %prog -H HOSTNAME [-w] [-c]"
parser = OptionParser(usage, version="%prog 1.0")
parser.add_option("-H", "--hostname", type="string", dest="hostname",
                  default="localhost", help="You may define a hostname with the -H option. \
                                             Default is: localhost.")
group = OptionGroup(parser, "Warning/critical thresholds",
                    "Use these options to set warning/critical thresholds \
                    for requests per second served by your Apache.")
group.add_option("-w", "--warning",
                 type="int",
                 dest="warning",
                 default=-2,
                 help="Use this option if you want to use warning/critical \
                        thresholds. Make sure to set a critical value as well. \
                        Default is: -1.")
group.add_option("-c",
                 "--critical",
                 type="int",
                 dest="critical",
                 default=-1,
                 help="Use this option if you want to use warning/critical \
                  thresholds. Make sure to set a warning value as \
                  well. Default is: -2.")

parser.add_option_group(group)

(options, args) = parser.parse_args()

hostname = options.hostname
warning = options.warning
critical = options.critical


def end(status, message):
    """Exits the script with the first argument as the return code and the
       second as the message to generate output."""

    if status == OK:
        print("OK: %s" % message)
        sys.exit(0)
    elif status == WARNING:
        print("WARNING: %s" % message)
        sys.exit(1)
    elif status == CRITICAL:
        print("CRITICAL: %s" % message)
        sys.exit(2)
    else:
        print("UNKNOWN: %s" % message)
        sys.exit(3)


def validate_thresholds(warning, critical):
    """Validates warning and critical thresholds in several ways."""

    if critical != -1 and warning == -2:
        end(UNKNOWN, "Please also set a warning value when using warning/" +
            "critical thresholds!")
    if critical == -1 and warning != -2:
        end(UNKNOWN, "Please also set a critical value when using warning/" +
            "critical thresholds!")
    if critical <= warning:
        end(UNKNOWN, "When using thresholds the critical value has to be " +
            "higher than the warning value. Please adjust your " +
            "thresholds.")


def temp_hum():
    global data, result
    try:
        # create an HTML Session object
        session = HTMLSession()

        # Use the object above to connect to needed webpage
        resp = session.get("http://" + hostname + "/graphic/envDsLocDisp.htm")
        # Run JavaScript code on webpage
        resp.html.render()
        option_tags = resp.html.find("td")
        values = [tag.text for tag in option_tags]

        data = []
        result = []
        for a in values:
            data.append(''.join(filter(str.isdigit, a)))

        result = [data[17], data[21]]

    except:
        end(CRITICAL, "Error retrieving data")

    return result

# main
if __name__ == "__main__":
    if critical != -1 or warning != -2:
        validate_thresholds(warning, critical)

    values = temp_hum()

    if critical != -1 and warning != -2:
        if int(values[0]) >= critical:
            end(CRITICAL, "Apache serves 1")
        elif warning <= int(values[0]) <= critical:
            end(WARNING, "Apache serves 2")
        else:
            end(OK, "HVAC temperature : %s C and Humidity Value is: %s ." % (values[0], values[1]))
    else:
        end(OK, "HVAC temperature : %s C and Humidity Value is: %s ." % (values[0], values[1]))