###  Codes to readout information from the VME modules directly using V1718

#### Prerequisites : These must be installed and be available for use in python

> caen_vme_lib
> ROOT

#### To get the base addresses of the VME boards connected to V1718 :

```
python Read_VME_board_base_addresses.py
``` 
This reads and lists the base addresses of the VME boards connected to V1718


#### To read out information from V792N (QDC) module
```
python Readloop.py
```

Enter the time duration for taking the data.

The Readloop.py module uses the process_flow_test.py module to read the data.


