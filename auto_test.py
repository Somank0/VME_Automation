from dataclasses import dataclass, field
import sys
import csv
import time
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser


from caen_libs import caenvme as vme
print("Library version:", vme.lib.sw_release())

# # Parse arguments
# parser = ArgumentParser(
#     description=__doc__,
#     formatter_class=ArgumentDefaultsHelpFormatter,
# )
#
# # Shared parser for subcommands
# parser.add_argument('-b', '--boardtype', type=str, help='board type', required=True, choices=tuple(i.name for i in vme.BoardType))
# parser.add_argument('-l', '--linknumber', type=str, help='link number, PID or hostname (depending on connectiontype)', required=True)
# parser.add_argument('-n', '--conetnode', type=int, help='CONET node', default=0)
#
# args = parser.parse_args()

boardtype = vme.BoardType["V1718"]
linknumber = "0"
conetnode = 0

# print("Available board types:")
# for bt in vme.BoardType:
#     print(f"- {bt.name}")
#
# while True:
#     boardtype_input = input("Enter board type: ").strip()
#     if boardtype_input in vme.BoardType.__members__:
#         boardtype = vme.BoardType[boardtype_input]
#         break
#     else:
#         print("Invalid board type. Please try again.")
#
# linknumber = input("Enter link number (usually '0' for USB): ").strip()
#
# try:
#     conetnode = int(input("Enter CONET node [default 0]: ") or "0")
# except ValueError:
#     print("Invalid CONET node. Defaulting to 0.")
#     conetnode = 0



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

    def write_cycle(self):
        """Write cycle"""
        print(f'VME base address: {self.__vme_base_address:08x}')
        print(f'Address modifier: {self.__address_modifier.name}')
        print(f'Data width: {self.__data_width.name}')
        try:
            address = int(input('Set address: 0x'), 16)
            value = int(input('Set value: 0x'), 16)
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



with vme.Device.open(boardtype, linknumber, conetnode) as device:
    demo = InteractiveDemo(device)

    demo.set_vme_baseaddress("B990000")
    time.sleep(0.1)
    demo.set_address_modifier("A24_U_DATA")
    time.sleep(0.1)
    # demo.set_data_width("D32")
    # time.sleep(0.5)

    # Output CSV path
    csv_filename = "vme_data_output.csv"
    valid_data_count = 0
    max_count = 100
    output_data = []

    print("Starting data acquisition...")
    # Save collected data to CSV
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Data"])

    while valid_data_count < max_count:
        # Step 1: Read the status register
        demo.set_data_width("D16")
        time.sleep(0.1)
        status_word = demo.read_cycle("1022")
        if status_word is None:
            continue

        # Step 2: Check bit 0 (data available)
        if not status_word & 0x2:
            # Read from output buffer at address 0x0000

            demo.set_data_width("D32")
            time.sleep(0.1)
            data_word = demo.read_cycle("0000")
            if data_word is None:
                continue

            # Check if bits 24–26 are 0
            if (data_word >> 24) & 0x7 == 0:
                output_data.append(data_word)
                valid_data_count += 1
                print(f"[{valid_data_count}] Data accepted: {data_word:08X}")
                time.sleep(0.1)
                with open(csv_filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    for i, val in enumerate(output_data):
                        writer.writerow([i + 1, f"{val:08X}"])
            else:
                print("Data rejected due to bits 24-26")

        # Optional: Sleep briefly to avoid CPU hogging
        time.sleep(10)

    # Save collected data to CSV
    # with open(csv_filename, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(["Data"])
    #     for i, val in enumerate(output_data):
    #         writer.writerow([i + 1, f"{val:08X}"])

    print(f"Data acquisition complete. {valid_data_count} entries saved to {csv_filename}")







