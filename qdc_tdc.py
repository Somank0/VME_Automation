
# Author : Archana Naik & Somanko Saha

import sys
sys.path.append('C:/Users/seemalab/Desktop/Root/root_v6.36.000/lib')  # Path to ROOT libraries (for Windows)
import ROOT
import array

import datetime

from base_functions import *
import time

boardtype = vme.BoardType["V1718"] #communication bridge board name
linknumber = "0"
conetnode = 0

def Setup_QDC(demo) :
    demo.set_vme_baseaddress("990000") #base address of QDC module
    time.sleep(0.1)
    demo.set_address_modifier("A24_U_DATA")
    time.sleep(0.1)
    demo.set_data_width("D16")
    time.sleep(1)
    demo.write_cycle("1032", "4") #clearing the data by writing to the "bit set 2 register"
    time.sleep(0.1)
    demo.write_cycle("1034", "4") #disabling the "bit set 2" enabled bit by writing to the "bit clear 2" register
    time.sleep(0.1)
    demo.write_cycle("1040", "0") #clearing the event counter register
    time.sleep(1)
    print("Clearing counter")

def Setup_TDC(demo) :
    demo.set_vme_baseaddress("DD0000") #base address of QDC module
    time.sleep(0.1)
    demo.set_address_modifier("A24_U_DATA")
    time.sleep(0.1)
    demo.set_data_width("D16")
    time.sleep(1)
    demo.write_cycle("1032", "4") #clearing the data by writing to the "bit set 2 register"
    time.sleep(0.1)
    demo.write_cycle("1034", "4") #disabling the "bit set 2" enabled bit by writing to the "bit clear 2" register
    time.sleep(0.1)
    demo.write_cycle("1040", "0") #clearing the event counter register
    time.sleep(1)
    print("Clearing counter")
    demo.write_cycle("1060", "0x19")  # Set largest FSR = 1.2 μs
    time.sleep(0.1)
    
def Readout_QDC_VME(demo) :

    demo.set_vme_baseaddress("990000") #base address of QDC module
    time.sleep(0.1)
    demo.set_address_modifier("A24_U_DATA")
    time.sleep(0.1)
    demo.set_data_width("D16")
    time.sleep(0.1)
    status_word = demo.read_cycle("1022")
    print("status word: ",status_word)
    if status_word is None:
        print("Empty QDC status_word")

    # Step 2: Check bit 0 (data available)
    elif status_word & 0x80:          
        # Read from output buffer at address 0x0000

        demo.set_data_width("D32")
        time.sleep(0.1)
        data_word = demo.read_cycle("0000")
        print("QDC data word: ",data_word)
        if data_word is None:
            print("Empty QDC data word")

        # Check if bits 24–26 are 0
        elif (data_word >> 24) & 0x7 == 0:
            top_bits = (data_word >> 24) & 0x7
            return data_word
        elif (data_word >> 24) & 0x7 == 4:
            counter=data_word & 0xFFFFFF
            print(f"QDC Counter : {counter}")
        else:
            print("QDC Data rejected due to bits 24-26")
            

            # Optional: Sleep briefly to avoid CPU hogging
    time.sleep(0.5)      

def Readout_TDC_VME(demo) :
    demo.set_vme_baseaddress("DD0000") #base address of QDC module
    time.sleep(0.1)
    demo.set_address_modifier("A24_U_DATA")
    time.sleep(0.1)
    demo.set_data_width("D16")
    time.sleep(0.1)
    status_word = demo.read_cycle("1022")
    print("status word: ",status_word)
    if status_word is None:
        print("Empty TDC status word")         
    # Step 2: Check bit 0 (data available)
    elif status_word & 0x80:          
    # Read from output buffer at address 0x0000
        demo.set_data_width("D32")               
        time.sleep(0.1)
        data_word = demo.read_cycle("0000")
        print("TDC data word: ",data_word)
        if data_word is None:
            print("Empty TDC data word")

        # Check if bits 24–26 are 0
        if (data_word >> 24) & 0x7 == 0:
            top_bits = (data_word >> 24) & 0x7
            return data_word
                    
        elif (data_word >> 24) & 0x7 == 4:
            counter=data_word & 0xFFFFFF
            print(f"TDC Counter : {counter}")
        else:
            print("TDC Data rejected due to bits 24-26")
    time.sleep(0.5)


# Get number of iterations from the user
num_iterations = int(input("Enter the number of iterations: "))

# Get input for the target module once
duration = float(input("Enter duration for the aquisition: "))
for i in range(num_iterations):
    print(f"\n--- Running iteration {i+1} --- Each iteration is {duration} seconds.")
    with vme.Device.open(boardtype, linknumber, conetnode) as device:
        demo = InteractiveDemo(device)
        Setup_QDC(demo)
        Setup_TDC(demo)
        time.sleep(1)
        start_time = time.time()
        while time.time() - start_time < duration :
            TDC_data_point= Readout_TDC_VME(demo)
            QDC_data_point =Readout_QDC_VME(demo)
            print("TDC data",TDC_data_point)
            print("QDC data",QDC_data_point)
        

print("\nAll iterations completed!")