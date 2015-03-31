# -*- coding: utf-8 -*-

# Copyright 2008-2012, 2014, 2015 Richard Dymond (rjdymond@gmail.com)
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

try:
    from microsphere import MicrosphereHtmlWriter, MicrosphereAsmWriter, Udg
except ImportError:
    from .microsphere import MicrosphereHtmlWriter, MicrosphereAsmWriter, Udg

class SkoolDazeHtmlWriter(MicrosphereHtmlWriter):
    def init(self):
        MicrosphereHtmlWriter.init(self)
        self.init_lessons(224, 255)
        self.init_characters(152, 169)
        self.font_address = 55552
        self._calculate_tap_index(65152, 222)

    def get_skool_udg(self, y, x, show_chars=False):
        ref_page = y + 152
        attr_addr = x + 128 + 256 * ref_page
        ref_addr = x + 256 * ref_page
        ref = self.snapshot[ref_addr]
        attr = self.snapshot[attr_addr]
        udg_page = 128 + 8 * (x // 32)
        udg_addr = ref + 256 * udg_page
        udg_bytes = self.snapshot[udg_addr:udg_addr + 2048:256]
        skool_udg = Udg(attr, udg_bytes, attr_addr=attr_addr, ref_addr=ref_addr, ref=ref, udg_page=udg_page, x=x, y=y)
        return skool_udg

    def get_sprite_udg(self, state, attr, row, col, udg_page=None):
        if udg_page is None:
            udg_page = 201 if 71 < (state & 127) < 104 else 185
        ref_page = 173 + col * 4 + row
        return self._get_sprite_udg(state, attr, ref_page, udg_page)

    def get_initial_states(self):
        initial_states = []
        for c in list(range(18)) + [20]:
            initial_states.append((self.snapshot[56064 + c], self.snapshot[56320 + c], self.snapshot[56576 + c]))
        return initial_states

    def keypress_table_rows(self, cwd):
        rows = []
        for c in range(32, 128):
            address = c + 26624
            offset = self.snapshot[address]
            lookup = offset + 26624
            key_byte = self.snapshot[lookup]
            routine = self.snapshot[lookup + 1] + 256 * self.snapshot[lookup + 2]
            subs = {
                'index': c,
                'key': self.get_chr(c),
                'address': address,
                'offset': offset,
                'lookup': lookup,
                'keycode': 'SPACE' if key_byte == 32 else chr(key_byte),
                'routine': '#R{}'.format(routine),
                'purpose': self.keypress_routines[routine]
            }
            rows.append(self.format_template('keypress_table_row', subs))
        return '\n'.join(rows)

    def _animatory_state_row(self, cwd, state):
        subs = {
            'state_l': state,
            'state_r': state + 128,
            'desc': self.as_descs.get(state, '-'),
            'img_l1': self.as_img(cwd, state, 2, 1, 120, 185),
            'img_r1': self.as_img(cwd, state + 128, 2, 1, 120, 185),
            'img_l2': self.as_img(cwd, state, 2, 1, 120, 201),
            'img_r2': self.as_img(cwd, state + 128, 2, 1, 120, 201)
        }
        return self.format_template('animatory_state_row', subs)

    def _get_animatory_state_tiles_row(self, n):
        states = ((n, 185), (n + 128, 185), (n, 201), (n + 128, 201))
        states_desc = '{0}, {1}: {2}'.format(n, n + 128, self.as_descs[n])
        return [(states, states_desc)]

    def place_char(self, cwd, char_num, x=None, y=None, state=None):
        base_addr = 55912 + char_num
        if state is not None:
            self.snapshot[base_addr] = state
        if x is not None:
            self.snapshot[base_addr + 256] = x
        if y is not None:
            self.snapshot[base_addr + 512] = y

    def hide_chars(self, cwd=None):
        for char_num in range(152, 173):
            self.place_char(cwd, char_num, 128)

class SkoolDazeAsmWriter(MicrosphereAsmWriter):
    pass
