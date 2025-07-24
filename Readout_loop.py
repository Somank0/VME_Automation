# Author : Archana Naik & Somanko Saha

import process_flow_test as pft
import sys
sys.path.append('C:/Users/seemalab/Desktop/Root/root_v6.36.000/lib')

# Get number of iterations from the user
num_iterations = int(input("Enter the number of iterations: "))

# Get input for the target module once
duration = float(input("Enter duration for the aquisition: "))
for i in range(num_iterations):
    print(f"\n--- Running iteration {i+1} --- Each iteration is {duration} seconds.")
    pft.Readout_QDC_VME(duration)

print("\nAll iterations completed!")
