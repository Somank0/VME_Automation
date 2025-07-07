import ROOT
import sys
import array
import os

def add_last12bits_branch(input_filename, tree_name):
    # Open file in update mode
    infile = ROOT.TFile.Open(input_filename, "UPDATE")
    if not infile or infile.IsZombie():
        print(f"Error: Cannot open '{input_filename}'!")
        return

    intree = infile.Get(tree_name)
    if not intree:
        print(f"Error: TTree '{tree_name}' not found in '{input_filename}'!")
        return

    # Setup to read existing branch
    qdc_val = array.array('I', [0])
    if intree.SetBranchAddress("Raw_count", qdc_val) < 0:
        print("Error: Branch 'Raw_count' not found in the tree!")
        return

    # Create a new tree with same structure + one new branch
    newtree = intree.CloneTree(0)  # Clone structure (no data)

    # New branch for last 12 bits in decimal (from binary string)
    last12bits = array.array('I', [0])
    newtree.Branch("Last12Bits_Decimal", last12bits, "Last12Bits_Decimal/i")

    # Loop through entries and fill the new tree
    nentries = intree.GetEntries()
    for i in range(nentries):
        intree.GetEntry(i)

        binary_str = format(qdc_val[0], '032b')
        last_12 = binary_str[-12:]
        last12bits[0] = int(last_12, 2)

        newtree.Fill()

        print(f"[{i}] Raw: 0x{qdc_val[0]:08X} | Bin: {binary_str} | Last12: {last_12} | Dec: {last12bits[0]}")

    # Overwrite the original tree with new one
    infile.cd()
    newtree.Write(tree_name, ROOT.TObject.kOverwrite)
    infile.Close()

    print(f"Done! New branch 'Last12Bits_Decimal' added to tree '{tree_name}' in file '{input_filename}'.")

# Entry point
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_last12bits_branch.py <root_filename> <tree_name>")
        sys.exit(1)

    filename = sys.argv[1]
    treename = sys.argv[2]

    add_last12bits_branch(filename, treename)
