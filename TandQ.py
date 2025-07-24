# Author: Archana Naik & Somanko Saha

import sys
sys.path.append('C:/Users/seemalab/Desktop/Root/root_v6.36.000/lib')

import ROOT
import array
import datetime
from base_functions import *
import time

boardtype = vme.BoardType["V1718"]
linknumber = "0"
conetnode = 0

def Setup_QDC(demo):
    demo.set_vme_baseaddress("990000")
    demo.set_address_modifier("A24_U_DATA")
    demo.set_data_width("D16")
    demo.write_cycle("1032", "4")
    demo.write_cycle("1034", "4")
    demo.write_cycle("1040", "0")
    print("QDC Counter cleared")

def Setup_TDC(demo):
    demo.set_vme_baseaddress("DD0000")
    demo.set_address_modifier("A24_U_DATA")
    demo.set_data_width("D16")
    demo.write_cycle("1032", "4")
    demo.write_cycle("1034", "4")
    demo.write_cycle("1040", "0")
    demo.write_cycle("1060", "0x19")
    print("TDC Counter cleared")

def Readout_QDC_VME(demo) :
    demo.set_vme_baseaddress("990000")
    demo.set_address_modifier("A24_U_DATA")
    demo.set_data_width("D16")
    status_word = demo.read_cycle("1022")

    if status_word is not None and (status_word & 0x80):
        demo.set_data_width("D32")
        data_word = demo.read_cycle("0000")

        if data_word is not None and ((data_word >> 24) & 0x7) == 0:
            return data_word
        else:
            print("QDC Data rejected due to bits 24-26")
    time.sleep(0.05)

def Readout_TDC_VME(demo) :
    demo.set_vme_baseaddress("DD0000")
    demo.set_address_modifier("A24_U_DATA")
    demo.set_data_width("D16")
    status_word = demo.read_cycle("1022")

    if status_word is not None and (status_word & 0x80):
        demo.set_data_width("D32")
        data_word = demo.read_cycle("0000")

        if data_word is not None and ((data_word >> 24) & 0x7) == 0:
           return data_word
        else:
            print("TDC Data rejected due to bits 24-26")
    time.sleep(0.05)


# Get user inputs
num_iterations = int(input("Enter the number of iterations: "))
duration = float(input("Enter duration for each acquisition (in seconds): "))

# Main acquisition loop
for i in range(num_iterations):
    print(f"\n--- Running iteration {i + 1} --- Each for {duration} seconds.")
    with vme.Device.open(boardtype, linknumber, conetnode) as device:
        demo = InteractiveDemo(device)
        Setup_QDC(demo)
        time.sleep(1)
        Setup_TDC(demo)
        time.sleep(1)

        start_time = time.time()
        TDC_data=[]
        QDC_data=[]
        while time.time() - start_time < duration:
            TDC_data.append(Readout_TDC_VME(demo))#, tdc_ch0_array, tdc_ch1_array, tdc_ch0_tree, tdc_ch1_tree)
            QDC_data.append(Readout_QDC_VME(demo))#, qdc_ch0_array, qdc_ch1_array, qdc_ch0_tree, qdc_ch1_tree)
        print("TDC data",TDC_data)
        print("QDC data",QDC_data)
