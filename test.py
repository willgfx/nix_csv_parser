import os
import sys
import unittest

import pyperclip

cmd = ''
if sys.platform == 'win32':
    cmd = 'nix_csv_parser.py'
else:
    cmd = './nix_csv_parser.py'

class NixCSVParserTests(unittest.TestCase):

    def run_cmd(self, cmd_line):
        print(cmd_line)
        os.system(cmd_line)

    def test_no_args(self):
        cmd_line = cmd
        print('### NO ARGS')
        self.run_cmd(cmd_line)

    def test_help(self):
        cmd_line = cmd + ' --help'
        print('### HELP')
        self.run_cmd(cmd_line)

    def test_version(self):
        cmd_line = cmd + ' --version'
        print('### VERSION')
        self.run_cmd(cmd_line)

    def test_csv_file_unsorted(self):
        cmd_line = cmd + ' test.csv'
        print('### FILE - UNSORTED')
        self.run_cmd(cmd_line)

    def test_csv_file_unsorted_wait(self):
        cmd_line = cmd + ' test.csv --wait 1'
        print('### FILE - UNSORTED - WAIT')
        self.run_cmd(cmd_line)

    def test_csv_file_sort_hue(self):
        cmd_line = cmd + ' test.csv --sort-hue'
        print('### FILE - HUE SORT')
        self.run_cmd(cmd_line)

    def test_csv_file_sort_sat(self):
        cmd_line = cmd + ' test.csv --sort-sat'
        print('### FILE - SAT SORT')
        self.run_cmd(cmd_line)

    def test_csv_file_sort_value(self):
        cmd_line = cmd + ' test.csv --sort-val'
        print('### FILE - VAL SORT')
        self.run_cmd(cmd_line)

    def test_clipboard_data(self):
        pyperclip.copy(
            'Color_Name,Description,L*,A*,B*,X,Y,Z,R,G,B,HEX,C,M,Y,K,ACES-R,ACES-G,ACES-B,ACEScg-R,ACEScg-G,ACEScg-B,Lin.sRGB-R,Lin.sRGB-G,Lin.sRGB-B\n'
            'B,,85.70,16.59,93.46,71.59,67.38,7.47,255,199,0,#FFC700,0%,26%,100%,0%,0.7645,0.5765,0.0696,0.9583,0.6126,0.0723,1.2470,0.5733,-0.0186,\n'
            'Y,,45.85,-52.60,14.94,7.45,15.16,10.50,0,128,82,#008052,99%,24%,86%,10%,0.0786,0.1803,0.0967,0.0506,0.1965,0.0961,-0.0439,0.2165,0.0842,\n'
            'X,,34.76,13.80,-40.90,9.57,8.38,28.82,55,78,147,#374E93,91%,79%,10%,1%,0.0977,0.0939,0.2643,0.0628,0.0766,0.2639,0.0376,0.0764,0.2929,\n'
            'A,,42.56,55.93,34.94,22.29,12.87,3.92,188,46,46,#BC2E2E,18%,96%,93%,8%,0.2373,0.0699,0.0359,0.3202,0.0605,0.0374,0.5052,0.0269,0.0276,\n'
            'Button BG,,44.20,-1.48,-1.17,13.06,13.98,15.74,101,105,106,#65696A,61%,50%,49%,18%,0.1373,0.1413,0.1445,0.1347,0.1413,0.1445,0.1298,0.1422,0.1451,\n'
            'Shell,,67.11,-0.24,3.06,34.89,36.78,37.54,165,163,158,#A5A39E,38%,31%,35%,0%,0.3675,0.3659,0.3448,0.3727,0.3679,0.3449,0.3781,0.3675,0.3413,\n'
            'D Pad,,35.63,-1.24,0.49,8.24,8.81,9.44,82,84,83,#525453,65%,55%,57%,32%,0.0867,0.0887,0.0867,0.0862,0.0890,0.0867,0.0844,0.0894,0.0864,\n'
            'Rear Label,,64.79,-1.15,7.27,31.79,33.78,31.32,161,157,144,#A19D90,39%,33%,42%,1%,0.3353,0.3344,0.2877,0.3458,0.3390,0.2879,0.3548,0.3386,0.2799,\n'
        )
        cmd_line = cmd + ' --clipboard'
        print('### CLIPBOARD DATA')
        self.run_cmd(cmd_line)

    def test_clipboard_path(self):
        pyperclip.copy('test.csv')
        cmd_line = cmd + ' --clipboard'
        print('### CLIPBOARD FILE PATH')
        self.run_cmd(cmd_line)

    def test_clipboard_html(self):
        pyperclip.copy(
            '<font color=#FFC700 size=72px>▄ </font><b>HEX:</b> #FFC700 - <b>RGB:</b> (255, 199, 0)<br>\n'
            '<font color=#008052 size=72px>▄ </font><b>HEX:</b> #008052 - <b>RGB:</b> (0, 128, 82)<br>\n'
            '<font color=#374E93 size=72px>▄ </font><b>HEX:</b> #374E93 - <b>RGB:</b> (55, 78, 147)<br>\n'
            '<font color=#BC2E2E size=72px>▄ </font><b>HEX:</b> #BC2E2E - <b>RGB:</b> (188, 46, 46)<br>\n'
            '<font color=#65696A size=72px>▄ </font><b>HEX:</b> #65696A - <b>RGB:</b> (101, 105, 106)<br>\n'
            '<font color=#A5A39E size=72px>▄ </font><b>HEX:</b> #A5A39E - <b>RGB:</b> (165, 163, 158)<br>\n'
            '<font color=#525453 size=72px>▄ </font><b>HEX:</b> #525453 - <b>RGB:</b> (82, 84, 83)<br>\n'
            '<font color=#A19D90 size=72px>▄ </font><b>HEX:</b> #A19D90 - <b>RGB:</b> (161, 157, 144)<br>\n'
        )
        cmd_line = cmd + ' --clipboard'
        print('### CLIPBOARD HTML')
        self.run_cmd(cmd)

    def test_no_data(self):
        cmd_line = cmd + ' --sort-hue'
        print('### NO DATA')
        self.run_cmd(cmd_line)

    def test_clipbaord_no_data(self):
        pyperclip.copy('nodata')
        cmd_line = cmd + ' --clipboard'
        print('### NO CLIPBOARD DATA')
        self.run_cmd(cmd_line)

    def test_bad_option_long(self):
        cmd_line = cmd + ' --badoption'
        print('### BAD OPTION - LONG')
        self.run_cmd(cmd_line)

    def test_bad_option_short(self):
        cmd_line = cmd + ' -x'
        print('### BAD OPTION - SHORT')
        self.run_cmd(cmd_line)

if __name__ == '__main__':
    unittest.main()
