from console import *
from pickle import dump, load

# Initialize a Network object
net = load(open('net.dmp', 'rb'))

# Load addons
net.load_addon('chess')

# Save the network
dump(net, open('net.dmp', 'wb'))
