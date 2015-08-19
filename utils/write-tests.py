#!/usr/bin/env python
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

SKOOL = '../sources/sd.skool'

SNAPSHOT = '../build/skool_daze.z80'

OUTPUT = """Using skool file: ../sources/sd.skool
Using ref files: ../sources/sd.ref, ../sources/sd-bugs.ref, ../sources/sd-changelog.ref, ../sources/sd-data.ref, ../sources/sd-facts.ref, ../sources/sd-glossary.ref, ../sources/sd-graphics.ref, ../sources/sd-pages.ref, ../sources/sd-pokes.ref
Parsing ../sources/sd.skool
Creating directory {odir}/skool_daze
Copying {SKOOLKIT_HOME}/skoolkit/resources/skoolkit.css to {odir}/skool_daze/skoolkit.css
Copying ../sources/sd.css to {odir}/skool_daze/sd.css
  Writing disassembly files in skool_daze/asm
  Writing skool_daze/maps/all.html
  Writing skool_daze/maps/routines.html
  Writing skool_daze/maps/data.html
  Writing skool_daze/maps/messages.html
  Writing skool_daze/buffers/gbuffer.html
  Writing skool_daze/graphics/graphics.html
  Writing skool_daze/graphics/playarea.html
  Copying ../sources/tiles.js to {odir}/skool_daze/tiles.js
  Writing skool_daze/graphics/patiles/patiles.html
  Writing skool_daze/graphics/asstart.html
  Writing skool_daze/graphics/as.html
  Writing skool_daze/graphics/astiles/astiles.html
  Writing skool_daze/buffers/cbuffer.html
  Writing skool_daze/lessons/timetables.html
  Writing skool_daze/lessons/index.html
  Writing skool_daze/lessons/224.html
  Writing skool_daze/lessons/225.html
  Writing skool_daze/lessons/226.html
  Writing skool_daze/lessons/227.html
  Writing skool_daze/lessons/228.html
  Writing skool_daze/lessons/229.html
  Writing skool_daze/lessons/230.html
  Writing skool_daze/lessons/231.html
  Writing skool_daze/lessons/232.html
  Writing skool_daze/lessons/233.html
  Writing skool_daze/lessons/234.html
  Writing skool_daze/lessons/235.html
  Writing skool_daze/lessons/236.html
  Writing skool_daze/lessons/237.html
  Writing skool_daze/lessons/238.html
  Writing skool_daze/lessons/239.html
  Writing skool_daze/lessons/240.html
  Writing skool_daze/lessons/241.html
  Writing skool_daze/lessons/242.html
  Writing skool_daze/lessons/243.html
  Writing skool_daze/lessons/244.html
  Writing skool_daze/lessons/245.html
  Writing skool_daze/lessons/246.html
  Writing skool_daze/lessons/247.html
  Writing skool_daze/lessons/248.html
  Writing skool_daze/lessons/249.html
  Writing skool_daze/lessons/250.html
  Writing skool_daze/lessons/251.html
  Writing skool_daze/lessons/252.html
  Writing skool_daze/lessons/253.html
  Writing skool_daze/lessons/254.html
  Writing skool_daze/lessons/255.html
  Writing skool_daze/tables/keys.html
  Writing skool_daze/graphics/glitches.html
  Writing skool_daze/reference/changelog.html
  Writing skool_daze/reference/bugs.html
  Writing skool_daze/reference/facts.html
  Writing skool_daze/reference/glossary.html
  Writing skool_daze/reference/pokes.html
  Parsing ../sources/load.skool
    Writing skool_daze/load/load.html
    Writing disassembly files in skool_daze/load
  Parsing ../sources/save.skool
    Writing skool_daze/save/save.html
    Writing disassembly files in skool_daze/save
  Parsing ../sources/start.skool
    Writing skool_daze/start/start.html
    Writing disassembly files in skool_daze/start
  Writing skool_daze/index.html"""

HTML_WRITER = '../sources:skooldaze.SkoolDazeHtmlWriter'

ASM_WRITER = '../sources:skooldaze.SkoolDazeAsmWriter'

write_tests(SKOOL, SNAPSHOT, OUTPUT, HTML_WRITER, ASM_WRITER)
