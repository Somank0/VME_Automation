from caen_libs import caenvme as vme

# Set up basic interactive demo wrapper
class InteractiveDemo:
    def __init__(self, device):
        self.device = device

    def read_cycle(self, address):
        return self.device.read_cycle(address, address_modifier=vme.A24_U_DATA, data_width=vme.D16)

    def write_cycle(self, address, value):
        return self.device.write_cycle(address, value, address_modifier=vme.A24_U_DATA, data_width=vme.D16)

# Open VME device
with vme.Device.open( vme.BoardType["V1718"],"0",0) as device:  # assuming no args needed
    demo = InteractiveDemo(device)

    for base in range(0x000000, 0xFF0000, 0x10000):
        try:
            val = demo.read_cycle(base + 0x1000)  # Firmware revision register
            print(f"Found V792 at base: 0x{base:06X}, Firmware: 0x{val:04X}")
        except Exception:
            continue
