
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

def Readout_QDC_VME(duration) :
    with vme.Device.open(boardtype, linknumber, conetnode) as device:
        demo = InteractiveDemo(device)

        demo.set_vme_baseaddress("DD0000") #base address of QDC module
        time.sleep(0.1)
        demo.set_address_modifier("A24_U_DATA")
        time.sleep(0.1)
        # demo.set_data_width("D32")
        # time.sleep(0.5)

        #================================================================
        def setup_v775n(demo):
            # Clear previous data
            demo.set_data_width("D16")
            demo.write_cycle("1032", "0004")  # Bit Set 2: Soft Clear
            time.sleep(0.1)
            demo.write_cycle("1034", "0004")  # Bit Clear 2: Release Clear
            time.sleep(0.1)

            # Set Common Stop mode (bit 10)
            demo.write_cycle("1032", "0400")  # Bit Set 2: Common Stop
            time.sleep(0.1)

            # Enable acquisition, BERR, and all channels (0x0483)
            demo.write_cycle("1010", "0483")
            time.sleep(0.1)

            # Confirm settings
            ctrl = demo.read_cycle("1010")
            print(f"[INFO] Control Register: 0x{ctrl:04X}")

            chan_mask = demo.read_cycle("1020")
            print(f"[INFO] Channel Enable Mask: 0x{chan_mask:04X}")

        # Read and decode one full event
        def read_event(demo):
            demo.set_data_width("D32")

            output = []
            print("[INFO] Waiting for event...")
            while True:
                status = demo.read_cycle("1022")
                if status is None:
                    continue
                if status & 0x80:  # Event Ready
                    print("[INFO] Event Ready!")
                    break
                time.sleep(0.05)

            # Read until End-of-Block (type 4)
            for i in range(32):
                word = demo.read_cycle("0000")
                if word is None:
                    continue

                word_type = (word >> 24) & 0x7
                if word_type == 0:
                    # TDC data word
                    channel = (word >> 17) & 0xF
                    tdc_value = word & 0xFFFF
                    print(f"[DATA] Channel {channel} TDC Value: {tdc_value}")
                    if channel == 1:
                        return tdc_value  # This is your desired channel
                elif word_type == 4:
                    print("[INFO] End of Block")
                    break
                else:
                    print(f"[SKIP] Word: 0x{word:08X}, type: {word_type}")

            return None

        # Main logic
        def measure_time_difference(demo):
            print("Started meeasure time function")
            setup_v775n(demo)
            print("Setup V775N")

            while True:
                print("Trying to read event")
                tdc_val = read_event(demo)
                print("TDC VAL",tdc_val)
                if tdc_val is not None:
                    # V775N is 12-bit, 50 ps/count typically
                    time_ps = tdc_val * 0.05  # assuming 50 ps/count
                    print(f"[RESULT] Time difference (Ch1 - Common): {tdc_val} bins = {time_ps:.1f} ps")
                time.sleep(0.5)
        print("Reading event")
        measure_time_difference(demo)
                #============================================================

        # Output CSV path
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_rootfile= "VME_TDC_data_"+ timestamp +".root"
        csv_filename = "vme_TDC_data_output_" + timestamp + ".csv"
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

        demo.set_data_width("D32")
        for i in range(10):
            word = demo.read_cycle("0000")
            if word is None:
                continue
            word_type = (word >> 24) & 0x7
            print(f"[{i}] Word: {word:08X}, type: {word_type}")


        demo.set_data_width("D16")
        time.sleep(1)
        #demo.write_cycle("1032", "4") #clearing the data by writing to the "bit set 2 register"
        #time.sleep(0.5)
        #demo.write_cycle("1034", "4") #disabling the "bit set 2" enabled bit by writing to the "bit clear 2" register
        #time.sleep(0.5)
        demo.write_cycle("1040", "0") #clearing the event counter register

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
            if not status_word & 0x2:          
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
            time.sleep(1)

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
    
Readout_QDC_VME(60)