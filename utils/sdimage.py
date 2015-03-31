#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse

# Use the current development version of SkoolKit
SKOOLKIT_HOME = os.environ.get('SKOOLKIT_HOME')
if not SKOOLKIT_HOME:
    sys.stderr.write('SKOOLKIT_HOME is not set; aborting\n')
    sys.exit(1)
if not os.path.isdir(SKOOLKIT_HOME):
    sys.stderr.write('SKOOLKIT_HOME={}; directory not found\n'.format(SKOOLKIT_HOME))
    sys.exit(1)
sys.path.insert(0, SKOOLKIT_HOME)

from skoolkit.image import ImageWriter
from skoolkit.snapshot import get_snapshot
from skoolkit.skoolhtml import Udg as BaseUdg, Frame

BLACKBOARDS = {
    'rr': {
        'geometry': (10, 5, 41, 2),
        'location': (48, 3),
        'tiles': range(35022, 35006, -1)
    },
    'wr': {
        'geometry': (10, 6, 25, 8),
        'location': (32, 10),
        'tiles': (
            33006, 33005, 33004, 33003, 33002, 33001, 35048, 35047,
            32998, 32997, 32996, 32995, 32994, 32993, 35040, 35039
         )
    },
    'er': {
        'geometry': (10, 6, 40, 8),
        'location': (47, 10),
        'tiles': range(35038, 35022, -1)
    }
}

def warn(text):
    sys.stderr.write('WARNING: {}\n'.format(text))

class Udg(BaseUdg):
    def __init__(self, attr, data, mask=None, x=None, y=None):
        BaseUdg.__init__(self, attr, data, mask)
        self.x = x
        self.y = y

class SkoolDaze:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.font_address = 55552

    def _get_sprite_udg(self, state, ref_page, udg_page):
        ref_addr = state + 256 * ref_page
        ref = self.snapshot[ref_addr]
        if ref == 0:
            data = [0] * 8
            mask = [255] * 8
        else:
            udg_addr = ref + 256 * udg_page
            data = self.snapshot[udg_addr:udg_addr + 4096:512]
            mask = self.snapshot[udg_addr + 256:udg_addr + 4352:512]
        return Udg(None, data, mask)

    def get_font_bitmap(self, character):
        base_address = ord(character) + self.font_address + 256
        width = self.snapshot[base_address - 256]
        return self.snapshot[base_address:base_address + 256 * width:256]

    def write(self, bb_tiles, words):
        udgs = [[0] * 8 for n in range(16)]
        for line_no, line in enumerate(words.split(r'\n')[:2]):
            columns = []
            for character in line:
                if columns or line_no == 0:
                    columns.append(0)
                columns.extend(self.get_font_bitmap(character))
            if len(columns) > 64:
                warn('Text overflows by {} pixel(s) on line {}'.format(len(columns) - 64, line_no + 1))
            for col, col_byte in enumerate(columns[:64]):
                udg = udgs[8 * line_no + col // 8]
                bit = 2 ** (7 - (col % 8))
                for b in range(8):
                    udg[7 - b] |= bit * (col_byte & 1)
                    col_byte //= 2
        for tile_addr, udg in zip(bb_tiles, udgs):
            for i, a in enumerate(range(tile_addr, tile_addr + 2048, 256)):
                self.snapshot[a] = udg[i] ^ 255

    def get_skool_udgs(self, x, y, w, h):
        skool_udgs = []
        for row in range(y, y + h):
            skool_udgs.append([])
            for col in range(x, x + w):
                skool_udgs[-1].append(self.get_skool_udg(row, col))
        self._superimpose_sprite_udgs(skool_udgs, x, y, w, h)
        return skool_udgs

    def _superimpose_sprite_udgs(self, udg_array, x, y, w, h):
        for state, char_x, char_y in self.get_states():
            x0 = char_x - x
            if x0 >= w:
                continue
            x1 = min(x0 + 3, w)
            if x1 < 0:
                continue
            x0 = max(x0, 0)
            y0 = char_y - y
            if y0 >= h:
                continue
            y1 = min(y0 + 4, h)
            if y1 < 0:
                continue
            y0 = max(y0, 0)
            for i in range(y0, y1):
                for j in range(x0, x1):
                    udg = udg_array[i][j]
                    sprite_udg = self.get_sprite_udg(state, udg.y - char_y, udg.x - char_x)
                    for k in range(8):
                        udg.data[k] = (udg.data[k] | sprite_udg.data[k]) & sprite_udg.mask[k]

    def get_skool_udg(self, y, x):
        ref_page = y + 152
        attr_addr = x + 128 + 256 * ref_page
        ref_addr = x + 256 * ref_page
        ref = self.snapshot[ref_addr]
        attr = self.snapshot[attr_addr]
        udg_page = 128 + 8 * (x // 32)
        udg_addr = ref + 256 * udg_page
        udg_bytes = self.snapshot[udg_addr:udg_addr + 2048:256]
        skool_udg = Udg(attr, udg_bytes, x=x, y=y)
        return skool_udg

    def get_sprite_udg(self, state, row, col):
        udg_page = 201 if 71 < (state & 127) < 104 else 185
        ref_page = 173 + col * 4 + row
        return self._get_sprite_udg(state, ref_page, udg_page)

    def get_states(self):
        return [self.snapshot[c + 56064:c + 56832:256] for c in range(21)]

    def place_char(self, char_num, x=None, y=None, state=None):
        base_addr = 55912 + char_num
        if state is not None:
            self.snapshot[base_addr] = state
        if x is not None:
            self.snapshot[base_addr + 256] = x
        if y is not None:
            self.snapshot[base_addr + 512] = y

    def hide_chars(self):
        for char_num in range(152, 173):
            self.place_char(char_num, 200)

def run(snafile, imgfname, options):
    snapshot = get_snapshot(snafile)
    skool = SkoolDaze(snapshot)
    width = 96
    eric = 172
    x = y = 0
    height = 21
    skool.hide_chars()

    if options.blackboard:
        bb = BLACKBOARDS[options.blackboard]
        width, height, x, y = bb['geometry']
        eric_x, eric_y = bb['location']
        skool.place_char(eric, eric_x, eric_y, 0)
    elif options.geometry:
        wh, xy = options.geometry.split('+', 1)
        width, height = [int(n) for n in wh.split('x')]
        x, y = [int(n) for n in xy.split('+')]

    for spec in options.text:
        board_id, sep, text = spec.partition(':')
        if sep:
            bb = BLACKBOARDS[board_id]
            skool.write(bb['tiles'], text)

    for spec in options.place_char:
        values = []
        for n in spec.split(','):
            try:
                values.append(int(n))
            except ValueError:
                values.append(None)
        skool.place_char(*values[:4])

    for spec in options.pokes:
        addr, val = spec.split(',', 1)
        step = 1
        if '-' in addr:
            addr1, addr2 = addr.split('-', 1)
            addr1 = int(addr1)
            if '-' in addr2:
                addr2, step = [int(i) for i in addr2.split('-', 1)]
            else:
                addr2 = int(addr2)
        else:
            addr1 = int(addr)
            addr2 = addr1
        addr2 += 1
        value = int(val)
        for a in range(addr1, addr2, step):
            snapshot[a] = value

    udg_array = skool.get_skool_udgs(x, y, width, height)
    frame = Frame(udg_array, options.scale)
    image_writer = ImageWriter()
    image_format = 'gif' if imgfname.lower()[-4:] == '.gif' else 'png'
    with open(imgfname, "wb") as f:
        image_writer.write_image([frame], f, image_format)

###############################################################################
# Begin
###############################################################################
parser = argparse.ArgumentParser(
    usage='sdimage.py [options] SNAPSHOT FILE.{png,gif}',
    description="Create an image from a snapshot of Skool Daze.",
    formatter_class=argparse.RawTextHelpFormatter,
    add_help=False
)
parser.add_argument('snapshot', help=argparse.SUPPRESS, nargs='?')
parser.add_argument('imgfname', help=argparse.SUPPRESS, nargs='?')
group = parser.add_argument_group('Options')
group.add_argument('-b', dest='blackboard', metavar='BOARD',
                   help="Create an image of Eric next to a blackboard; BOARD must be\n"
                        "one of:\n"
                        "  rr: Reading Room      er: Exam Room\n"
                        "  wr: White Room\n")
group.add_argument('-c', dest='place_char', metavar='C,X,Y[,S]', action='append', default=[],
                   help="Place character C at (X,Y) with animatory state S (this\n"
                        "option may be used multiple times); if X or Y is blank, that\n"
                        "coordinate is left unchanged\n"
                        "      172: Eric         166: Mr Creak\n"
                        "      169: Einstein     165: Mr Withit\n"
                        "      168: Angelface    164: Mr Rockitt\n"
                        "      167: Boy Wander   163: Mr Wacker\n"
                        "  152-162: Little boys")
group.add_argument('-g', dest='geometry', metavar='WxH+X+Y',
                   help='Create an image with this geometry')
group.add_argument('-p', dest='pokes', metavar='A[-B[-C]],V', action='append', default=[],
                   help="Do POKE N,V for N in {A, A+C, A+2C,...B} (this option may be\n"
                        "used multiple times)")
group.add_argument('-s', dest='scale', type=int, default=2,
                   help='Set the scale of the image (default: 2)')
group.add_argument('-w', dest='text', metavar='BOARD:TEXT', action='append', default=[],
                   help="Write text on a blackboard; use \\n for newline, and see the\n"
                        "-b option for a list of board identifiers (this option may be\n"
                        "used multiple times)")
namespace, unknown_args = parser.parse_known_args()
if unknown_args or not namespace.snapshot or not namespace.imgfname:
    parser.exit(2, parser.format_help())
run(namespace.snapshot, namespace.imgfname, namespace)
