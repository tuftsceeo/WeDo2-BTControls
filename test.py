# from WeDo import *
# import time

# hub = Smarthub('24:71:89:17:9D:AE')
# hub.connect()

# hub.attach_port(2, Motor)

# hub.get_port(2).set_speed(0.1)

# time.sleep(5)

# hub.get_port(2).set_speed(0)

# hub.disconnect()

CHARACTERISTIC_INPUT_VALUE_UUID = "0x1560"
CHARACTERISTIC_INPUT_FORMAT_UUID = "0x1561"
CHARACTERISTIC_INPUT_COMMAND_UUID = "0x1563"
CHARACTERISTIC_OUTPUT_COMMAND_UUID = "0x1565"

UUID_CUSTOM_BASE = "1212-EFDE-1523-785FEABCD123"
UUID_STANDARD_BASE = "0000-1000-8000-00805f9b34fb"


def uuid_with_prefix_custom_base(prefix):
    padding = add_leading_zeroes(prefix)
    return "{}-{}".format(padding, UUID_CUSTOM_BASE)


def uuid_with_prefix_standard_base(prefix):
    padding = add_leading_zeroes(prefix)
    return "{}-{}".format(padding, UUID_STANDARD_BASE)


def add_leading_zeroes(prefix):
    hex_prefix = "0x"
    if prefix[0:2] == hex_prefix:
        prefix = prefix[2:]

    return ("00000000" + prefix)[len(prefix):]

char_uuid = uuid_with_prefix_custom_base(CHARACTERISTIC_INPUT_VALUE_UUID)

print (char_uuid)