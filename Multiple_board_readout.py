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





# Main acquisition loop
def Acquisition() :
    # Get user inputs
    num_iterations = int(input("Enter the number of iterations: "))
    duration = float(input("Enter duration for each acquisition (in seconds): "))

    for i in range(num_iterations):
        print(f"\n--- Running iteration {i + 1} --- Each for {duration} seconds.")
        with vme.Device.open(boardtype, linknumber, conetnode) as device:
            demo = InteractiveDemo(device)
            Setup_QDC(demo)
            time.sleep(1)
            Setup_TDC(demo)
            time.sleep(1)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            outfile_name = f"VME_TDC_QDC_output_{timestamp}.root"
            outfile = ROOT.TFile(outfile_name, "RECREATE")
            # Arrays for branch
            tdc_val = array.array('I', [0])
            qdc_val = array.array('I', [0])

            # Trees
            TDC_tree = ROOT.TTree("TDC_tree", "TDC Valid Data")
            QDC_tree = ROOT.TTree("QDC_tree", "QDC Valid Data")

            TDC_tree.Branch("Raw_data", tdc_val, "Raw_data/i")
            QDC_tree.Branch("Raw_data", qdc_val, "Raw_data/i")


            start_time = time.time()
            tDC_data=[]
            qDC_data=[]
            while time.time() - start_time < duration:
                TDC_data=Readout_TDC_VME(demo)#, tdc_ch0_array, tdc_ch1_array, tdc_ch0_tree, tdc_ch1_tree)
                QDC_data=Readout_QDC_VME(demo)#, qdc_ch0_array, qdc_ch1_array, qdc_ch0_tree, qdc_ch1_tree)
                if TDC_data is not None:
                    tDC_data.append(TDC_data)
                    tdc_val[0] = TDC_data
                    TDC_tree.Fill()
                if QDC_data is not None:
                    qDC_data.append(QDC_data)
                    qdc_val[0] = QDC_data
                    QDC_tree.Fill()
                

            print("TDC data",tDC_data)
            print("QDC data",qDC_data)
            time.sleep(1)
        outfile.Write()
        outfile.Close()
        print(f"\nROOT file saved: VME_TDC_QDC_output_{timestamp}.root")

Acquisition()