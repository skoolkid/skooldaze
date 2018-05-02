#!/usr/bin/env python3
import sys
import os

SKOOLKIT_HOME = os.environ.get('SKOOLKIT_HOME')
if not SKOOLKIT_HOME:
    sys.stderr.write('SKOOLKIT_HOME is not set; aborting\n')
    sys.exit(1)
if not os.path.isdir(SKOOLKIT_HOME):
    sys.stderr.write('SKOOLKIT_HOME={}: directory not found\n'.format(SKOOLKIT_HOME))
    sys.exit(1)
sys.path.insert(0, '{}/tools'.format(SKOOLKIT_HOME))
from testwriter import write_tests

SKOOL = 'sd.skool'

SNAPSHOT = 'build/skool_daze.z80'

OUTPUT = """Using ref files: sd.ref, bugs.ref, changelog.ref, data.ref, facts.ref, glossary.ref, graphics.ref, pages.ref, pokes.ref
Parsing sd.skool
Output directory: {odir}/skool_daze
Copying {SKOOLKIT_HOME}/skoolkit/resources/skoolkit.css to skoolkit.css
Copying sd.css to sd.css
Writing disassembly files in asm
Writing maps/all.html
Writing maps/routines.html
Writing maps/data.html
Writing maps/messages.html
Writing buffers/gbuffer.html
Writing reference/bugs.html
Writing reference/changelog.html
Writing reference/facts.html
Writing reference/glossary.html
Writing graphics/glitches.html
Writing reference/pokes.html
Writing graphics/graphics.html
Writing graphics/playarea.html
Copying tiles.js to tiles.js
Writing graphics/patiles/patiles.html
Writing graphics/asstart.html
Writing graphics/as.html
Writing graphics/astiles/astiles.html
Writing buffers/cbuffer.html
Writing lessons/timetables.html
Writing lessons/index.html
Writing lessons/#N224.html
Writing lessons/#N225.html
Writing lessons/#N226.html
Writing lessons/#N227.html
Writing lessons/#N228.html
Writing lessons/#N229.html
Writing lessons/#N230.html
Writing lessons/#N231.html
Writing lessons/#N232.html
Writing lessons/#N233.html
Writing lessons/#N234.html
Writing lessons/#N235.html
Writing lessons/#N236.html
Writing lessons/#N237.html
Writing lessons/#N238.html
Writing lessons/#N239.html
Writing lessons/#N240.html
Writing lessons/#N241.html
Writing lessons/#N242.html
Writing lessons/#N243.html
Writing lessons/#N244.html
Writing lessons/#N245.html
Writing lessons/#N246.html
Writing lessons/#N247.html
Writing lessons/#N248.html
Writing lessons/#N249.html
Writing lessons/#N250.html
Writing lessons/#N251.html
Writing lessons/#N252.html
Writing lessons/#N253.html
Writing lessons/#N254.html
Writing lessons/#N255.html
Writing tables/keys.html
Parsing load.skool
Writing load/load.html
Writing disassembly files in load
Parsing save.skool
Writing save/save.html
Writing disassembly files in save
Parsing start.skool
Writing start/start.html
Writing disassembly files in start
Writing index.html"""

write_tests(SKOOL, SNAPSHOT, OUTPUT)
