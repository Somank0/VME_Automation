# Author : Archana Naik & Somanko Saha

import ROOT
import sys
import array
import os

def last_12_bits_to_decimal(dataword):
    return dataword & 0xFFF  # 0xFFF = 0b111111111111 = 12 bits

def get_channel_number(data_word):
    return (data_word >> 17) & 0x0F  # Use bits 17–20 (4 bits → channels 0–15)


def add_channel_branches(filename, treename):
    if not os.path.exists(filename):
        print(f" File not found: {filename}")
        return

    rootfile = ROOT.TFile(filename, "UPDATE")
    if not rootfile or rootfile.IsZombie():
        print(f" Could not open ROOT file: {filename}")
        return

    input_tree = rootfile.Get(treename)
    if not input_tree:
        print(f" Tree '{treename}' not found in {filename}")
        rootfile.Close()
        return


    # Read original data branch
    original_branch_name = input_tree.GetListOfBranches()[0].GetName()
    original_val = array.array('I', [0])
    input_tree.SetBranchAddress(original_branch_name, original_val)
    
    new_tree = input_tree.CloneTree(0)


    # Set up new branches
    ch_data = {}
    for ch in range(16):  # Channels 0–15 based on 4-bit range
        ch_data[ch] = array.array('I', [0])
        new_tree.Branch(f"ch_{ch}", ch_data[ch], f"ch_{ch}/i")

    raw_copy = array.array('I', [0])
    new_tree.Branch("Raw_data", raw_copy, "Raw_data/i")
    print(ch_data)

    

    # Loop and fill branches

    for i in range(input_tree.GetEntries()):
        input_tree.GetEntry(i)
        data = original_val[0]
        raw_copy[0] = data

        # Reset all branches
        for ch in range(16):
            ch_data[ch][0] = 0

        ch_num = get_channel_number(data)
        print(ch_num)
        if 0 <= ch_num < 16:
            ch_data[ch_num][0] = last_12_bits_to_decimal(data)
            
        new_tree.Fill()

    # Write updated tree
    rootfile.cd()
    new_tree.Write(treename, ROOT.TObject.kOverwrite)
    rootfile.Close()
    print(f" Branches ch_0 to ch_15 added to tree '{treename}' in file '{filename}'.")


'''
# ---------- Command-line Usage ----------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_channel_branches_bit17to20.py <file.root> <tree_name>")
        sys.exit(1)

    filename = sys.argv[1]
    treename = sys.argv[2]
    add_channel_branches(filename, treename)
'''
#add_last12bits_branch("VME_TDC_QDC_output_20250722_154734.root", "TDC_tree", "Raw_TDC")
#add_channel_branches("VME_TDC_QDC_output_20250723_165339.root", "QDC_tree")
add_channel_branches("VME_TDC_QDC_output_20250724_112140_2hr.root", "QDC_tree")
