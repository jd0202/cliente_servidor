from email.headerregistry import Address
import sys
from uuid import getnode as get_mac

inarg=sys.argv
address = hex(get_mac())[2:]
print('-'.join(address[i:i+2] for i in range(0, len(address), 2)))