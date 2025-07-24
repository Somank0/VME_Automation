
# Author : Bapi Basak & Shashank
from dataclasses import dataclass, field
import sys
import csv
import time

from caen_libs import caenvme as vme
print("Library version:", vme.lib.sw_release())





print('------------------------------------------------------------------------------------')
print(f'CAEN VMELib binding loaded (lib version {vme.lib.sw_release()})')
print('------------------------------------------------------------------------------------')


@dataclass
class InteractiveDemo:
    """Interactive demo for CAEN VMELib"""

    device: vme.Device

    # Private fields
    __vme_base_address: int = field(default=0)
    __address_modifier: vme.AddressModifiers = field(default=vme.AddressModifiers.A32_U_DATA)
    __data_width: vme.DataWidth = field(default=vme.DataWidth.D32)

    def set_vme_baseaddress(self,  base_addr=None):
        """Set VME base address"""
        print(f'Current value: {self.__vme_base_address:08x}')
        try:
            self.__vme_base_address = int(base_addr, 16)
        except ValueError as ex:
            print(f'Invalid value: {ex}')

    def set_address_modifier(self, addr_mode):
        """Set address modifier"""
        print(f'Current value: {self.__address_modifier.name}')
        try:
            self.__address_modifier = vme.AddressModifiers[addr_mode]
        except KeyError as ex:
            print(f'Invalid value: {ex}')

    def set_data_width(self, data_width):
        """Set data width"""
        print(f'Current value: {self.__data_width.name}')
        try:
            self.__data_width = vme.DataWidth[data_width]
        except KeyError as ex:
            print(f'Invalid value: {ex}')

    def read_cycle(self, read_addr):
        """Read cycle"""
        print(f'VME base address: {self.__vme_base_address:08x}')
        print(f'Address modifier: {self.__address_modifier.name}')
        print(f'Data width: {self.__data_width.name}')
        try:
            address = int(read_addr, 16)
        except ValueError as ex:
            print(f'Invalid input: {ex}')
            return
        try:
            value = self.device.read_cycle(self.__vme_base_address | address, self.__address_modifier, self.__data_width)
        except vme.Error as ex:
            print(f'Failed: {ex}')
            return
        print(f'Value: {value:08x}')
        return value

    def write_cycle(self, write_addr, write_data):
        """Write cycle"""
        print(f'VME base address: {self.__vme_base_address:08x}')
        print(f'Address modifier: {self.__address_modifier.name}')
        print(f'Data width: {self.__data_width.name}')
        try:
            address = int(write_addr, 16)
            value = int(write_data, 16)
        except ValueError as ex:
            print(f'Invalid input: {ex}')
            return
        try:
            self.device.write_cycle(self.__vme_base_address | address, value, self.__address_modifier, self.__data_width)
        except vme.Error as ex:
            print(f'Failed: {ex}')

    def read_register(self):
        """Read register"""
        try:
            address = int(input('Set address: 0x'), 16)
        except ValueError as ex:
            print(f'Invalid input: {ex}')
            return
        try:
            value = self.device.registers[address]
        except vme.Error as ex:
            print(f'Failed: {ex}')
            return
        print(f'Value: {value:08x}')

    def write_register(self):
        """Write register"""
        try:
            address = int(input('Set address: 0x'), 16)
            value = int(input('Set value: 0x'), 16)
        except ValueError as ex:
            print(f'Invalid input: {ex}')
            return
        try:
            self.device.registers[address] = value
        except vme.Error as ex:
            print(f'Failed: {ex}')

    def blt_read_cycle(self):
        """BLT read cycle"""
        print(f'VME base address: {self.__vme_base_address:08x}')
        print(f'Address modifier: {self.__address_modifier.name}')
        print(f'Data width: {self.__data_width.name}')
        try:
            address = int(input('Set address: 0x'), 16)
            size = int(input('Set size: '))
        except ValueError as ex:
            print(f'Invalid input: {ex}')
            return
        try:
            buffer = self.device.blt_read_cycle(self.__vme_base_address | address, size, self.__address_modifier, self.__data_width)
        except vme.Error as ex:
            print(f'Failed: {ex}')
            return
        print('Buffer:')
        for value in buffer:
            print(value)


def _quit():
    """Quit"""
    print('Quitting...')
    sys.exit()