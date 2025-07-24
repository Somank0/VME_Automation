import pyvisa

rm = pyvisa.ResourceManager()

resources = [
    'TCPIP0::192.168.0.66::inst0::INSTR',
    'ASRL1::INSTR'
]

for resource in resources:
    print(f"\nTrying resource: {resource}")
    try:
        instr = rm.open_resource(resource)
        # Query the instrument ID (common for most instruments)
        idn = instr.query('*IDN?')
        print(f"Response from {resource}: {idn}")
    except Exception as e:
        print(f"Failed to communicate with {resource}")
        print(f"Error: {e}")
