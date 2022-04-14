# mcp990x.py - driver class for the I2C based Microchip MCP990x temperature sensors family

"""This module allows driving the I2C temp sensor"""
import smbus

class Temperature:
    def __init__(self, value, unit="celsius"):
        k = value
        if unit.lower() in ["celsius", "c"]:
            k = self.celsius_to_kelvin(value)
        elif unit.lower() in ["fahrenheit", "f"]:
            k = self.fahrenheit_to_kelvin(value)
        elif unit.lower() in ["kelvin", "k"]:
            pass
        else:
            raise ValueError("unknown unit %s", str(unit))
        self._kelvin = k

    def __repr__(self):
        return str(self.celsius)

    def kelvin_to_celsius(self, value):
        return value - 273.15

    def kelvin_to_fahrenheit(self, value):
        return 1.8*self.kelvin_to_celsius(value) + 32

    def celsius_to_kelvin(self, value):
        return value + 273.15

    def fahrenheit_to_kelvin(self, value):
        return (value - 32)/1.8

    @property
    def k(self):
        return self._kelvin

    @property
    def kelvin(self):
        return self._kelvin

    @property
    def c(self):
        return self.celsius

    @property
    def celsius(self):
        return self.kelvin_to_celsius(self.kelvin)

    @property
    def f(self):
        return self.fahrenheit

    @property
    def fahrenheit(self):
        return self.kelvin_to_fahrenheit(self.kelvin)

assert(Temperature(0, "c").fahrenheit == 32)
assert(Temperature(0, "k").c == -273.15)
assert(Temperature(0, "c").k == 273.15)

def reading_to_temperature(arr) -> Temperature:
    # stitch together the temp reading bytes: the total data is 11 bits,
    # with the most significant 8 in the high reg and the least significant 3
    # in the top 3 bits of the low reg. So, OR them together as a 17 bits integer,
    # then shift everything right by 5
    # arr[1] = arr[1]>>5
    # temp = int.from_bytes(arr, byteorder="big", signed=True) + 0.125
    temp = ((arr[0] << 8 | arr[1]) >> 5) * 0.125
    return Temperature(temp, "c")

class Sensor(object):
    """Sensor([bus]) -> Sensor
    Return a new Sensor object that is connected to the
    specified I2C device interface.
    """
    REG_ADDR_TEMP_HIGH = 0x00
    REG_ADDR_TEMP_LOW = 0x29

    REG_ADDR_EXT1_TEMP_HIGH = 0x01
    REG_ADDR_EXT1_TEMP_LOW = 0x10

    REG_ADDR_EXT2_TEMP_HIGH = 0x23
    REG_ADDR_EXT2_TEMP_LOW = 0x24

    REG_ADDR_EXT3_TEMP_HIGH = 0x2a
    REG_ADDR_EXT3_TEMP_LOW = 0x2b

    REG_ADDR_LAST = 0xFF

    _bus = None
    _debug = False
    _i2c_addr = 0b1001100

    def __init__(self, bus=0,  preinited_bus=None, debug=False, i2c_addr=0b1001100):
        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1), etc
        if preinited_bus is not None:
            if debug:
                print("using preinited-bus, address {0}".format(i2c_addr))
            self._bus = preinited_bus
        else:
            if debug:
                print("init-ing bus {0}, address {1}".format(bus, i2c_addr))
            self._bus = smbus.SMBus(bus)
        self._debug = debug
        self._i2c_addr = i2c_addr

    def close(self):
        """close()
        Disconnects the object from the bus.
        """
        self._bus.close()
        self._bus = None

    def __write_register(self, reg_addr, values):
        """ this writes a 8 bit register pointed to by reg_addr.
        """
        if self._bus is None:
            raise IOError("Bus not open")
        if reg_addr > self.REG_ADDR_LAST:
            raise IOError("Invalid register address {0}".format(reg_addr))
        if len(values) > 1:
            raise IOError("Invalid data length {0}".format(len(values)))

        self._bus.write_i2c_block_data(self._i2c_addr, reg_addr, values)

    def __read_register(self, reg_addr):
        """ this reads a 8 bit register pointed to by reg_addr
        """
        if self._bus is None:
            raise IOError("Bus not open")
        if reg_addr > self.REG_ADDR_LAST:
            raise IOError("Invalid register address {0}".format(reg_addr))

        return self._bus.read_byte_data(self._i2c_addr, reg_addr)

    def read(self, channel=0):
        """read()
        read the current temperature
        """
        if channel == 0:
            data = [self.__read_register(self.REG_ADDR_TEMP_HIGH), self.__read_register(self.REG_ADDR_TEMP_LOW)]
        elif channel == 1:
            data = [
                self.__read_register(self.REG_ADDR_EXT1_TEMP_HIGH),
                self.__read_register(self.REG_ADDR_EXT1_TEMP_LOW)]
        elif channel == 2:
            data = [
                self.__read_register(self.REG_ADDR_EXT2_TEMP_HIGH),
                self.__read_register(self.REG_ADDR_EXT2_TEMP_LOW)]
        elif channel == 3:
            data = [
                self.__read_register(self.REG_ADDR_EXT3_TEMP_HIGH),
                self.__read_register(self.REG_ADDR_EXT3_TEMP_LOW)]
        else:
            raise ValueError("Unknown channel %s", channel)

        # stitch together the temp reading bytes: the total data is 11 bits,
        # with the most significant 8 in the high reg and the least significant 3
        # in the top 3 bits of the low reg. So, OR them together as a 17 bits integer,
        # then shift everything right by 5
        if self._debug:
            for reg in data:
                print("reg: " + hex(reg))

        temp = reading_to_temperature(data)
        if self._debug:
            print(str(temp))

        return temp
