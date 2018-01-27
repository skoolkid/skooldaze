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

SKOOL = 'sources/sd.skool'

SNAPSHOT = 'build/skool_daze.z80'

OUTPUT = """Using skool file: sources/sd.skool
Using ref files: sources/sd.ref, sources/bugs.ref, sources/changelog.ref, sources/data.ref, sources/facts.ref, sources/glossary.ref, sources/graphics.ref, sources/pages.ref, sources/pokes.ref
Parsing sources/sd.skool
Creating directory {odir}/skool_daze
Copying {SKOOLKIT_HOME}/skoolkit/resources/skoolkit.css to {odir}/skool_daze/skoolkit.css
Copying sources/sd.css to {odir}/skool_daze/sd.css
  Writing disassembly files in skool_daze/asm
  Writing skool_daze/maps/all.html
  Writing skool_daze/maps/routines.html
  Writing skool_daze/maps/data.html
  Writing skool_daze/maps/messages.html
  Writing skool_daze/buffers/gbuffer.html
  Writing skool_daze/reference/bugs.html
  Writing skool_daze/reference/changelog.html
  Writing skool_daze/reference/facts.html
  Writing skool_daze/reference/glossary.html
  Writing skool_daze/graphics/glitches.html
  Writing skool_daze/reference/pokes.html
  Writing skool_daze/graphics/graphics.html
  Writing skool_daze/graphics/playarea.html
  Copying sources/tiles.js to {odir}/skool_daze/tiles.js
  Writing skool_daze/graphics/patiles/patiles.html
  Writing skool_daze/graphics/asstart.html
  Writing skool_daze/graphics/as.html
  Writing skool_daze/graphics/astiles/astiles.html
  Writing skool_daze/buffers/cbuffer.html
  Writing skool_daze/lessons/timetables.html
  Writing skool_daze/lessons/index.html
  Writing skool_daze/lessons/#N224.html
  Writing skool_daze/lessons/#N225.html
  Writing skool_daze/lessons/#N226.html
  Writing skool_daze/lessons/#N227.html
  Writing skool_daze/lessons/#N228.html
  Writing skool_daze/lessons/#N229.html
  Writing skool_daze/lessons/#N230.html
  Writing skool_daze/lessons/#N231.html
  Writing skool_daze/lessons/#N232.html
  Writing skool_daze/lessons/#N233.html
  Writing skool_daze/lessons/#N234.html
  Writing skool_daze/lessons/#N235.html
  Writing skool_daze/lessons/#N236.html
  Writing skool_daze/lessons/#N237.html
  Writing skool_daze/lessons/#N238.html
  Writing skool_daze/lessons/#N239.html
  Writing skool_daze/lessons/#N240.html
  Writing skool_daze/lessons/#N241.html
  Writing skool_daze/lessons/#N242.html
  Writing skool_daze/lessons/#N243.html
  Writing skool_daze/lessons/#N244.html
  Writing skool_daze/lessons/#N245.html
  Writing skool_daze/lessons/#N246.html
  Writing skool_daze/lessons/#N247.html
  Writing skool_daze/lessons/#N248.html
  Writing skool_daze/lessons/#N249.html
  Writing skool_daze/lessons/#N250.html
  Writing skool_daze/lessons/#N251.html
  Writing skool_daze/lessons/#N252.html
  Writing skool_daze/lessons/#N253.html
  Writing skool_daze/lessons/#N254.html
  Writing skool_daze/lessons/#N255.html
  Writing skool_daze/tables/keys.html
  Parsing sources/load.skool
    Writing skool_daze/load/load.html
    Writing disassembly files in skool_daze/load
  Parsing sources/save.skool
    Writing skool_daze/save/save.html
    Writing disassembly files in skool_daze/save
  Parsing sources/start.skool
    Writing skool_daze/start/start.html
    Writing disassembly files in skool_daze/start
  Writing skool_daze/index.html"""

HTML_WRITER = 'sources:skooldaze.SkoolDazeHtmlWriter'

ASM_WRITER = 'sources:skooldaze.SkoolDazeAsmWriter'

write_tests(SKOOL, SNAPSHOT, OUTPUT, HTML_WRITER, ASM_WRITER)
