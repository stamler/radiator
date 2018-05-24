# (c) 2018 Dean Stamler
# Extract the set of manufacturers from a directory of log files
# created by radiator.vbs. Log files are not moved or modified.

from glob import iglob
from os import path
from helpers import InventoryLogFile
from sys import argv

def build_manufacturers_set(search_path):
    mfgs = set()
    linecount = 0
    for f in iglob(path.join(search_path,'**/*.log'), recursive=True):
        ilf = InventoryLogFile(f)
        ilf.filehandle.seek(0)
        for line in ilf.filehandle:
            # This loop is not being entered
            linecount += 1
            m = ilf.regex.match(line)
            mfgs.add(m.group(3))
    return (mfgs, linecount)

try:
    arg = argv[1]
except IndexError:
    arg = None
if (arg is None):
    print("\n  Usage: manufacturers.py <search_path>\n")
else:
    mfgs, lines = build_manufacturers_set(arg)
    print('scanned {} lines for {} manufacturers'.format( lines, len(mfgs) ))
    print("\"" + "\"\n\"".join(mfgs) + "\"" )
