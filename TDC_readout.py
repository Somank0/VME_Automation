
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

#Code to get fixed number of qdc output data. Change max_count to required number of events.
#output will be a .csv file

#duration = float(input("Enter duration in seconds: "))

duration=0

def Readout_TDC_VME(duration) :
    with vme.Device.open(boardtype, linknumber, conetnode) as device:
        demo = InteractiveDemo(device)

        demo.set_vme_baseaddress("DD0000") #base address of QDC module
        time.sleep(0.1)
        demo.set_address_modifier("A24_U_DATA")
        time.sleep(0.1)
        # demo.set_data_width("D32")
        # time.sleep(0.5)

        # Output CSV path
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_rootfile= "VME_TDC_data_2hr_new_"+ timestamp +".root"
        csv_filename = "vme_TDC_data_output_2hr_new_" + timestamp + ".csv"
        valid_data_count = 0
        max_count = 10
        output_data = []
    
        print("Starting data acquisition...")
        # Save collected data to CSV

        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Data"])
        
        outfile=ROOT.TFile(output_rootfile,"recreate")
        tree = ROOT.TTree("T", "")
        count = array.array('I',[0])
        tree.Branch("Raw_count",count,"Raw_count/i")

        demo.set_data_width("D16")
        time.sleep(1)
        demo.write_cycle("1032", "4") #clearing the data by writing to the "bit set 2 register"
        time.sleep(0.5)
        demo.write_cycle("1034", "4") #disabling the "bit set 2" enabled bit by writing to the "bit clear 2" register
        time.sleep(0.5)
        demo.write_cycle("1040", "0") #clearing the event counter register
        time.sleep(1)
        print("Clearing counter")


        ###setting fsr
        demo.set_data_width("D16")
        demo.write_cycle("1060", "0x1E")  # Set largest FSR = 1.2 μs
        time.sleep(0.1)


        start_time = time.time()
        #while valid_data_count <max_count:
        while time.time() - start_time < duration:
            # Step 1: Read the status register
            demo.set_data_width("D16")
            time.sleep(0.1)
            status_word = demo.read_cycle("1022")
            print("status word: ",status_word)
            if status_word is None:
                continue

            # Step 2: Check bit 0 (data available)
            if status_word & 0x80:          
                # Read from output buffer at address 0x0000

                demo.set_data_width("D32")

                
                time.sleep(0.1)
                data_word = demo.read_cycle("0000")
                print("data word: ",data_word)
                if data_word is None:
                    continue

                # Check if bits 24–26 are 0
                if (data_word >> 24) & 0x7 == 0:
                    output_data.append(data_word)
                    valid_data_count += 1
                    print(f"[{valid_data_count}] Data accepted: {data_word:08X}")
                    count[0]=data_word
                    top_bits = (data_word >> 24) & 0x7
                    tree.Fill()
                    time.sleep(0.1)
                    with open(csv_filename, mode='w', newline='') as file:
                        writer = csv.writer(file)
                        for i, val in enumerate(output_data):
                            writer.writerow([i + 1, f"{val:08X}"])
                elif (data_word >> 24) & 0x7 == 4:
                    counter=data_word & 0xFFFFFF
                    print(f"Counter : {counter}")




                else:
                    print("Data rejected due to bits 24-26")

            # Optional: Sleep briefly to avoid CPU hogging
            time.sleep(0.1)

        tree.Write()
        outfile.Close()
        """
        demo.set_data_width("D32")
        time.sleep(0.1)
        data_word = demo.read_cycle("0000")
        counter = -1  # Initialize counter with default value
    
        if(data_word >> 24) & 0x7 == 4:
            counter = data_word & 0xFFFFFF
        #else: counter=-1
        """

        #print(f"Data acquisition complete. {valid_data_count} entries saved to {csv_filename}, counter value {int(counter) + 1}, Time ={duration}")#counter counts from 0
        #print(f"Data acquisition complete. {valid_data_count} entries saved to {csv_filename}, Time ={duration}")#counter counts from 0
        return 0
    
Readout_TDC_VME(3600)