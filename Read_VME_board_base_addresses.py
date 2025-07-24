import time
from caen_libs import caenvme as vme

class VMEInterface:
    def __init__(self, device):
        self.device = device
        self.base = 0
        self.am = 0x39
        self.dw = 0x02

    def set_base_address(self, base_addr_hex):
        self.base = int(base_addr_hex, 16)

    def read_register(self, offset_hex_str):
        offset = int(offset_hex_str, 16)
        return self.device.read_cycle(self.base + offset, self.am, self.dw)

def scan_vme_bus():
    boardtype = 0
    linknumber = 0
    conetnode = 0

    with vme.Device.open(boardtype, linknumber, conetnode) as device:
        vme_if = VMEInterface(device)

        print("🔍 Scanning for VME modules (including V1751)...")
        found_modules = []

        for base in range(0x000000, 0xFF0000, 0x10000):
            try:
                vme_if.set_base_address(f"{base:06X}")
                time.sleep(0.01)
                val = vme_if.read_register("1000")  # firmware revision register

                if val is not None:
                    print(f" Module found at 0x{base:06X}, Firmware revision: 0x{val:04X}")
                    found_modules.append((base, val))
            except Exception as e:
                if "BUS_ERROR" in str(e):
                    continue  # Skip empty slots
                else:
                    print(f" Error at 0x{base:06X}: {e}")

        if not found_modules:
            print("No VME modules detected.")
        else:
            print(f"\n Total modules found: {len(found_modules)}")

if __name__ == "__main__":
    scan_vme_bus()