import ROOT
import sys
import array

def extract_last12bits_as_decimal(input_filename, tree_name):
    # Open input ROOT file
    infile = ROOT.TFile.Open(input_filename)
    if not infile or infile.IsZombie():
        print(f"Error: Cannot open '{input_filename}'!")
        return

    intree = infile.Get(tree_name)
    if not intree:
        print(f"❌ Error: TTree '{tree_name}' not found in '{input_filename}'!")
        return

    # Setup for reading QDC_Value
    qdc_val = array.array('I', [0])  # 'I' = unsigned int
    intree.SetBranchAddress("Raw_count", qdc_val)

    # Prepare output ROOT file and tree
    output_filename = f"binary_last12bits_{input_filename}"
    outfile = ROOT.TFile(output_filename, "RECREATE")
    outtree = ROOT.TTree("T", "Last 12 bits (binary->decimal)")

    last12bits_decimal = array.array('I', [0])
    outtree.Branch("Last12Bits_Decimal", last12bits_decimal, "Last12Bits_Decimal/i")

    # Loop through entries
    for i in range(intree.GetEntries()):
        intree.GetEntry(i)
        val = qdc_val[0]

        # Convert to binary string (padded to 32 bits)
        binary_str = format(val, '032b')
        last12 = binary_str[-12:]  # Get last 12 bits as string

        # Convert last 12 bits to decimal
        last12bits_decimal[0] = int(last12, 2)

        print(f"Entry {i} | QDC_Value: 0x{val:08X} | Binary: {binary_str} | Last 12: {last12} | Decimal: {last12bits_decimal[0]}")
        outtree.Fill()

    outtree.Write()
    outfile.Close()
    infile.Close()

    print(f"Done! Saved as '{output_filename}' with TTree 'T' and branch 'Last12Bits_Decimal'.")

# Entry point
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_last12bits_from_binary.py <input_root_file> <tree_name>")
        sys.exit(1)

    input_filename = sys.argv[1]
    tree_name = sys.argv[2]

    extract_last12bits_as_decimal(input_filename, tree_name)
