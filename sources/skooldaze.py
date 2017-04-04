# Copyright 2008-2015, 2017 Richard Dymond (rjdymond@gmail.com)
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

import html

from skoolkit.graphics import Frame, Udg as BaseUdg
from skoolkit.skoolhtml import HtmlWriter, join
from skoolkit.skoolasm import AsmWriter
from skoolkit.skoolmacro import parse_ints, parse_brackets

def parse_as(text, index):
    end, state = parse_ints(text, index, 1, (None,))
    end, link_text = parse_brackets(text, end, '#N{}'.format(state))
    return end, state, link_text

def parse_lesson(text, index):
    end, lesson = parse_ints(text, index, 1)
    end, link_text = parse_brackets(text, end, '#N{}'.format(lesson))
    return end, lesson, link_text

def parse_s(text, index):
    sep = text[index]
    end, s = parse_brackets(text, index, '', sep, sep)
    return end, '#IF({{case}}==1){0}{0}{1}{0}{2}{0}{0}'.format(sep, s.lower(), s)

class SkoolDazeHtmlWriter(HtmlWriter):
    def init(self):
        self.char_buf_descs = self.get_sections('CharBuf', True)
        self.keypress_routines = self.get_dictionary('KeypressRoutines')
        self.as_descs = self.get_dictionary('AnimatoryStates')
        self.characters = self.get_dictionary('Characters')
        self.lesson_descs = self.get_dictionary('Lessons')
        self.min_lesson = 224
        self.max_lesson = 255
        self.min_character = 152
        self.max_character = 169
        self.font_address = 55552
        self._calculate_tap_index(65152, 222)
        self.b_fmt = '{:02X}' if self.base == 16 else '{}'
        self.w_fmt = '{:04X}' if self.base == 16 else '{}'
        if self.case == 1:
            self.b_fmt = self.b_fmt.lower()
            self.w_fmt = self.w_fmt.lower()

    def _calculate_tap_index(self, tap_address_table, max_tap):
        min_tap = tap_address_table % 256
        self.tap_addresses = {}
        self.tap_descs = {}
        for t in range(min_tap, max_tap + 1, 2):
            address = tap_address_table + t - min_tap
            tap_address = self.snapshot[address] + 256 * self.snapshot[address + 1]
            tap_entry = self.get_entry(tap_address)
            if tap_entry:
                sep_index = tap_entry.description.index(':')
                self.tap_descs[t] = tap_entry.description[sep_index + 1:].strip()
                self.tap_addresses[t] = tap_address

    def _get_sprite_udg(self, state, attr, ref_page, udg_page):
        ref_addr = state + 256 * ref_page
        ref = self.snapshot[ref_addr]
        if ref == 0:
            # These must be lists so that the UDG can be flipped or rotated
            # in-place
            udg = [0, 0, 0, 0, 0, 0, 0, 0]
            mask = [255, 255, 255, 255, 255, 255, 255, 255]
        else:
            udg_addr = ref + 256 * udg_page
            udg = self.snapshot[udg_addr:udg_addr + 4096:512]
            mask = self.snapshot[udg_addr + 256:udg_addr + 4352:512]
        return Udg(attr, udg, mask, ref_addr=ref_addr, ref=ref, udg_page=udg_page)

    def get_chr(self, code):
        if code == 127:
            return '&#169;'
        if code == 94:
            return '&#8593;'
        if code == 96:
            return '&#163;'
        return html.escape(chr(code), False)

    def build_sprite(self, state, attr=None, udg_page=None):
        udg_array = []
        for row in range(4):
            udg_array.append([self.get_sprite_udg(state, attr, row, col, udg_page) for col in range(3)])
        return udg_array

    def get_font_bitmap(self, character):
        base_address = ord(character) + self.font_address + 256
        width = self.snapshot[base_address - 256]
        return self.snapshot[base_address:base_address + 256 * width:256]

    def get_text(self, words):
        columns = []
        for character in words:
            columns.append(0)
            columns.extend(self.get_font_bitmap(character))
        udg_array = []
        for col in range(len(columns)):
            col_byte = columns[col]
            udg_index = col // 8
            bit = 2**(7 - (col - 8 * udg_index))
            if udg_index == len(udg_array):
                udg_array.append([0] * 8)
            udg = udg_array[udg_index]
            for b in range(8):
                udg[7 - b] |= bit * (col_byte & 1)
                col_byte //= 2
        return udg_array

    def _font_udgs(self, address, num_chars):
        first_char = address % 256
        udgs = self.get_text(''.join([chr(c) for c in range(first_char, first_char + num_chars)]))
        return [[Udg(56, udg) for udg in udgs]]

    def font(self, cwd, address, num_chars=96, scale=2, fname='font'):
        width = scale * (sum(self.snapshot[address:address + num_chars]) + num_chars + 1)
        frame = Frame(lambda: self._font_udgs(address, num_chars), scale, width=width)
        return self.handle_image([frame], fname, cwd, path_id='FontImagePath')

    def _draw_text(self, udgs, words, x, y):
        text_udgs = self.get_text(words)
        for col in range(len(text_udgs)):
            udg = udgs[y][col + x].data
            for index in range(8):
                udg[index] |= text_udgs[col][index]

    def get_skool_udgs(self, x, y, w, h, show_chars=False, show_x=0):
        skool_udgs = []
        for row in range(y, y + h):
            skool_udgs.append([])
            for col in range(x, x + w):
                skool_udgs[-1].append(self.get_skool_udg(row, col, show_chars))
        if show_chars:
            self._superimpose_sprite_udgs(skool_udgs, x, y, w, h)
        if show_x is not None and show_x > 0:
            line = [Udg(8 * (7 - skool_x % 2), [0] * 8) for skool_x in range(x, x + w)]
            for skool_x in range(x, x + w):
                if skool_x % show_x == 0:
                    self._draw_text([line], str(skool_x), skool_x - x, 0)
            skool_udgs.insert(0, line)
            skool_udgs.append(line)
        return skool_udgs

    def _superimpose_sprite_udgs(self, udg_array, x, y, w, h):
        for state, char_x, char_y in self.get_initial_states():
            x0 = char_x - x
            if x0 >= w:
                continue
            x1 = min((x0 + 3, w))
            if x1 < 0:
                continue
            x0 = max((x0, 0))
            y0 = char_y - y
            if y0 >= h:
                continue
            y1 = min((y0 + 4, h))
            if y1 < 0:
                continue
            y0 = max((y0, 0))
            for i in range(y0, y1):
                for j in range(x0, x1):
                    udg = udg_array[i][j]
                    sprite_udg = self.get_sprite_udg(state, None, udg.y - char_y, udg.x - char_x)
                    for k in range(8):
                        udg.data[k] = (udg.data[k] | sprite_udg.data[k]) & sprite_udg.mask[k]

    def as_img(self, cwd, num, scale=2, mask=1, attr=120, udg_page=None, fname_suffix=''):
        mask_infix = 'm' if mask else 'u'
        udg_page_infix = udg_page if udg_page is not None else ''
        snapshot_name = self.get_snapshot_name()
        snapshot_infix = '_{0}'.format(snapshot_name) if snapshot_name else ''
        fname = 'as{0:03d}_{1}x{2}{3}{4}{5}{6}'.format(num & 255, attr, scale, mask_infix, udg_page_infix, snapshot_infix, fname_suffix)
        frame = Frame(lambda: self.build_sprite(num, attr, udg_page), scale, mask)
        alt = "Animatory state {}".format(num & 255)
        return self.handle_image([frame], fname, cwd, alt, 'AnimatoryStateImagePath')

    def play_area(self, cwd, fname, x, y, w=1, h=1, scale=2, show_chars=0, show_x=0):
        frame = Frame(lambda: self.get_skool_udgs(x, y, w, h, show_chars, show_x), scale)
        return self.handle_image([frame], fname, cwd, path_id='PlayAreaImagePath')

    def write_playarea_tile_table(self, cwd, tiles, prefix='s'):
        lines = []
        for row in tiles:
            cells = []
            for tile in row:
                if tile:
                    img_fname = '{0:x}{1:x}.{2}'.format(tile.udg_addr, tile.attr, self.default_image_format)
                    img_path = join(cwd, img_fname)
                    if self.need_image(img_path):
                        self.write_image(img_path, [[tile]], scale=4)
                    subs = {
                        'x': tile.x,
                        'x_offset': self.b_fmt.format(128),
                        'y': tile.y,
                        'y_offset': self.b_fmt.format(152),
                        'ref_addr': self.w_fmt.format(tile.ref_addr),
                        'ref': self.b_fmt.format(tile.ref),
                        'udg_page': self.b_fmt.format(tile.udg_page),
                        'udg_addr': self.w_fmt.format(tile.udg_addr),
                        'attr_addr': self.w_fmt.format(tile.attr_addr),
                        'attr': self.b_fmt.format(tile.attr),
                        'img_fname': img_fname
                    }
                    cells.append(self.format_template('play_area_tile', subs))
                else:
                    cells.append(self.format_template('play_area_tile_blank', {}))
            lines.append(self.format_template('play_area_tile_row', {'tiles': '\n'.join(cells)}))
        return self.format_template('play_area_tiles', {'rows': '\n'.join(lines)})

    def play_area_tiles(self, cwd, w, h):
        return self.write_playarea_tile_table(cwd, self.get_skool_udgs(0, 0, w, h))

    def animatory_states(self, cwd):
        return '\n'.join([self._animatory_state_row(cwd, n) for n in range(128)])

    def _get_sprite_tile_img_fname(self, tile, state):
        return '{0:x}.{1}'.format(tile.udg_addr, self.default_image_format)

    def astiles(self, cwd):
        rows = []
        attr = 120
        for n in range(128):
            for state_specs, states_desc in self._get_animatory_state_tiles_row(n):
                frames = []
                for state, udg_page in state_specs:
                    tiles = []
                    sprite = self.build_sprite(state, attr, udg_page)
                    num_rows = len(sprite)
                    for row_num in range(num_rows):
                        row = sprite[row_num]
                        for col_num in range(len(row)):
                            tile = row[col_num]
                            bubble_id_suffix = '{0:02x}'.format(udg_page) if udg_page is not None else ''
                            bubble_id = 'B{0:02x}{1:x}{2}'.format(state, row_num + num_rows * col_num, bubble_id_suffix)
                            img_fname = self._get_sprite_tile_img_fname(tile, state)
                            img_path = join(cwd, img_fname)
                            if self.need_image(img_path):
                                self.write_image(img_path, [[tile]], scale=4, mask=1)
                            template_name = 'astile' if tile.ref else 'astile_null'
                            astile_subs = {
                                'bubble_id': bubble_id,
                                'state': self.b_fmt.format(state),
                                'row': row_num,
                                'column': col_num,
                                'img_fname': img_fname,
                                'lsb': self.b_fmt.format(tile.ref_addr % 256),
                                'ref_page': self.b_fmt.format(tile.ref_addr // 256),
                                'ref_addr': self.w_fmt.format(tile.ref_addr),
                                'ref': self.b_fmt.format(tile.ref),
                                'udg_page': self.b_fmt.format(tile.udg_page),
                                'udg_addr': self.w_fmt.format(tile.udg_addr)
                            }
                            tiles.append(self.format_template(template_name, astile_subs))
                    template_name = 'astiles_frame_{}x{}'.format(num_rows, len(row))
                    frames.append(self.format_template(template_name, {'tiles': tiles}))
                astiles_row_subs = {'frames': '\n'.join(frames), 'desc': states_desc}
                rows.append(self.format_template('astiles_row', astiles_row_subs))
        return '\n'.join(rows)

    def lesson_index(self, cwd):
        lessons = []
        for i in range(self.min_lesson, self.max_lesson + 1):
            subs = {'type': i, 'description': self.lesson_descs[i]}
            lessons.append(self.format_template('lesson_type', subs))
        return '\n'.join(lessons)

    def lesson(self, cwd, lesson_num):
        timetables = []
        for c in range(self.min_character, self.max_character + 1):
            lesson_address = lesson_num + 256 * c
            tap = self.snapshot[lesson_address]
            subs = {
                'pt_address': self.min_lesson + 256 * c,
                'character_num': self.b_fmt.format(c),
                'character': self.characters[c],
                'lesson_address': self.w_fmt.format(lesson_address),
                'cl_num': self.b_fmt.format(tap),
                'cl_address': self.tap_addresses[tap],
                'cl_desc': self.tap_descs[tap]
            }
            timetables.append(self.format_template('timetable', subs))

        prev_href = next_href = ''
        if lesson_num > self.min_lesson:
            prev_href = self.relpath(cwd, self.paths['Lesson{}'.format(lesson_num - 1)])
        prev_lesson = {
            'num': self.b_fmt.format(lesson_num - 1),
            'exists': 1 if prev_href else 0,
            'href': prev_href
        }
        lesson = {
            'num': self.b_fmt.format(lesson_num),
            'desc': self.lesson_descs[lesson_num]
        }
        if lesson_num < self.max_lesson:
            next_href = self.relpath(cwd, self.paths['Lesson{}'.format(lesson_num + 1)])
        next_lesson = {
            'num': self.b_fmt.format(lesson_num + 1),
            'exists': 1 if next_href else 0,
            'href': next_href
        }
        subs = {
            'prev_lesson': prev_lesson,
            'lesson': lesson,
            'next_lesson': next_lesson,
            'm_timetable': '\n'.join(timetables)
        }
        return self.format_template('lesson', subs)

    def personal_timetables(self, cwd):
        lines = []
        for c in range(self.min_character, self.max_character + 1):
            subs = {
                'address': self.min_lesson + 256 * c,
                'num': self.b_fmt.format(c),
                'name': self.characters[c]
            }
            lines.append(self.format_template('personal_timetable', subs))
        return '\n'.join(lines)

    def cast(self, cwd):
        return self.format_template('cast', {'characters': self.characters})

    def cbuffer(self, cwd):
        cbuffer_bytes = []
        for byte_nums, entries in self.char_buf_descs:
            descs = [self.format_template('cbuffer_desc', {'desc': entry}) for entry in entries]
            row_descs = [self.format_template('cbuffer_desc_row', {'t_cbuffer_desc': desc}) for desc in descs[1:]]
            subs = {
                'rowspan': len(descs),
                'bytes': byte_nums,
                't_cbuffer_desc': descs[0],
                'm_cbuffer_desc_row': '\n'.join(row_descs)
            }
            cbuffer_bytes.append(self.format_template('cbuffer_bytes', subs))
        return self.format_template('cbuffer', {'m_cbuffer_bytes': '\n'.join(cbuffer_bytes)})

    def expand_as(self, text, index, cwd):
        # #AS[state][(link text)]
        end, state, link_text = parse_as(text, index)
        as_file = self.relpath(cwd, self.paths['AnimatoryStates'])
        anchor = '#{}'.format(state) if state is not None else ''
        link = self.format_link(as_file + anchor, self.expand(link_text))
        return end, link

    def expand_lesson(self, text, index, cwd):
        # #LESSONnum[(link text)]
        end, lesson, link_text = parse_lesson(text, index)
        page_id = 'Lesson{0}'.format(lesson)
        href = self.relpath(cwd, self.paths[page_id])
        link = self.format_link(href, self.expand(link_text))
        return end, link

    def expand_s(self, text, index, cwd):
        # #S/text/
        return parse_s(text, index)

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
                'index': '#N{}'.format(c),
                'key': self.get_chr(c),
                'address': '#N{}'.format(address),
                'offset': '#N{}'.format(offset),
                'lookup': '#N{}'.format(lookup),
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
            'state_l_s': self.b_fmt.format(state),
            'state_r_s': self.b_fmt.format(state + 128),
            'desc': self.as_descs.get(state, '-'),
            'img_l1': self.as_img(cwd, state, 2, 1, 120, 185),
            'img_r1': self.as_img(cwd, state + 128, 2, 1, 120, 185),
            'img_l2': self.as_img(cwd, state, 2, 1, 120, 201),
            'img_r2': self.as_img(cwd, state + 128, 2, 1, 120, 201)
        }
        return self.format_template('animatory_state_row', subs)

    def _get_animatory_state_tiles_row(self, n):
        states = ((n, 185), (n + 128, 185), (n, 201), (n + 128, 201))
        states_desc = '{0}, {0}: {{}}'.format(self.b_fmt).format(n, n + 128, self.as_descs[n])
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

class SkoolDazeAsmWriter(AsmWriter):
    def expand_as(self, text, index):
        # #AS[state][(link text)]
        end, state, link_text = parse_as(text, index)
        return end, self.expand(link_text)

    def expand_lesson(self, text, index):
        # #LESSONnum[(link text)]
        end, lesson, link_text = parse_lesson(text, index)
        return end, self.expand(link_text)

    def expand_s(self, text, index):
        # #S/text/
        return parse_s(text, index)

class Udg(BaseUdg):
    def __init__(self, attr, data, mask=None, attr_addr=None, ref_addr=None, ref=None, udg_page=None, x=None, y=None):
        BaseUdg.__init__(self, attr, data, mask)
        self.attr_addr = attr_addr
        self.ref_addr = ref_addr
        # We store the UDG reference now in case the snapshot changes before
        # the reference is looked up via self.snapshot[udg.ref_addr]
        self.ref = ref
        self.udg_page = udg_page
        self.udg_addr = None if udg_page is None else ref + 256 * udg_page
        self.x = x
        self.y = y
