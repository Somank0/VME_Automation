import ctypes

# ==================
# Config
# ==================
CAEN_DLL_PATH = r"C:/Program Files/CAEN/VME/lib/x86_64/CAENVMElib.dll"  # Update if needed

# Load CAEN VME DLL
caenvme = ctypes.windll.LoadLibrary(CAEN_DLL_PATH)

# Constants
CAEN_VME_USB = 0
BdNum = 0

handle = ctypes.c_int()
ret = caenvme.CAENVME_Init(CAEN_VME_USB, BdNum, 0, ctypes.byref(handle))

if ret != 0:
    print(f" Cannot open V1718 (error code {ret})")
    exit(1)

print(f" V1718 initialized successfully. Handle: {handle.value}")

found_boards = []

# =====================================
# A24 scan: 0x000000 to 0x00FFFFF
# =====================================
print(" Scanning A24 address space...")

a24_modifier = 0x39  # cvA24_U_DATA
data_width = 0x03    # D16
probe_offset = 0x1000

for base in range(0x000000, 0x00100000, 0x10000):  # step: 64 KB
    addr = base + probe_offset
    data = ctypes.c_ushort()
    ret = caenvme.CAENVME_ReadCycle(
        handle.value,
        addr,
        ctypes.byref(data),
        a24_modifier,
        data_width
    )
    if ret == 0:
        print(f" Board found at A24 base address: 0x{base:06X}")
        found_boards.append(("A24", base))
    else:
        pass

# =====================================
# A32 scan: 0x20000000 to 0x2FFFFFFF
# =====================================
print("🔎 Scanning A32 address space...")

a32_modifier = 0x09  # cvA32_U_DATA
data_width_32 = 0x0F  # D32
probe_offset_32 = 0x8140

for base in range(0x20000000, 0x30000000, 0x100000):  # step: 1 MB
    addr = base + probe_offset_32
    data = ctypes.c_uint()
    ret = caenvme.CAENVME_ReadCycle(
        handle.value,
        addr,
        ctypes.byref(data),
        a32_modifier,
        data_width_32
    )
    if ret == 0:
        print(f" Board found at A32 base address: 0x{base:08X}")
        found_boards.append(("A32", base))
    else:
        pass

if not found_boards:
    print(" No boards detected in scanned ranges. Check power, cables, and address settings.")

caenvme.CAENVME_End(handle.value)
print(" V1718 closed.")
