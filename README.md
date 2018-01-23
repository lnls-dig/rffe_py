# RFFE-py

Python library to communicate with the RFFE Box

## Usage

To communicate with the RFFE box, first you need to know its IP address and make sure that it's visible in network.
Then, open a python (either 2.7 or 3.4) interpreter or include in your script the following code (don't forget to change the IP address).

```python
from rffe-lib import *
RFFE = RFFEControllerBoard("10.2.118.200")
```

For example, in order to read the RF channels temperature:

```python
temp_ac = RFFE.get_temp_ac()
temp_bd = RFFE.get_temp_ac()
```

Set attenuators value:

```python
RFFE.set_attenuator_value(25.5)
```
