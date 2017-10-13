#!/usr/bin/env python3
# encoding: utf-8
# by Will Fuller, sinistergfx@gmail.com

"""Parses Nix Color Sensor CSV data, outputs HTML-based swatches to clipboard.
Defaults to using data or CSV file path from the clipboard.
Optionally sort output by hue, saturation, or value.

Created by Will Fuller, sinistergfx@gmail.com"""

import time
import csv
import colorsys
import argparse

import pyperclip

VERSION = '2.1.0 (2017.10.12)'
SWATCH_CHAR = '▄'
SWATCH_SIZE = '72px'


def exit_wait(wait=0):
    """Optionally wait N seconds before exiting"""

    time.sleep(wait)
    exit()


def messager(msg, extra_info='', exit_after=False, wait=0):
    """Central message handling, optionally exit after display"""

    messages = {
        'error_clipboard_nodata':
            'Error: No CSV data found in clipboard.\n',
        'error_nodata':
            'Error: No CSV data provided.\n',
        'error_sort':
            'Error: Unrecognized sort type: %s\n' % extra_info,
        'info_tryhelp':
            "Try 'nix_csv_parser.py --help' for more information\n",
        'status_clipboard':
            'Reading CSV data from clipboard...\n',
        'status_file':
            'Reading CSV data from %s...\n' % extra_info,
        'status_html':
            'HTML data found instead, no problem...\n'
    }

    if isinstance(msg, list):
        for item in msg:
            print(messages[item])
    elif isinstance(msg, str):
        print(messages[msg])

    if exit_after:
        exit_wait(wait)


class Swatch():
    """Hold swatch values, generate HTML output"""

    hex_value = ''
    rgb_value = (0, 0, 0)
    html = ''

    def __init__(self, hex_value, rgb_value):
        self.hex_value = hex_value

        if rgb_value is not None:
            self.rgb_value = rgb_value
        else:
            # Derive rgb value from hex if not provided
            red, green, blue = bytes.fromhex(hex_value[1:])
            self.rgb_value = (red, green, blue)

        self.set_html()


    def set_html(self):
        """Generate swatch output HTML"""

        self.html = (
            '<font color=%s size=%s>%s </font>'
            '<b>HEX:</b> %s - <b>RGB:</b> %s<br>\n' % (
                self.hex_value, SWATCH_SIZE, SWATCH_CHAR,
                self.hex_value, str(self.rgb_value)
            )
        )


    def print(self):
        """Output swatch data to console"""

        print('  %s HEX: %s - RGB: %s' % (
            SWATCH_CHAR, self.hex_value, self.rgb_value
        ))


class CSVParser():
    """Parse Nix CSV data from file or clipboard"""

    mode = 'file'
    csv_file = None
    swatches = []
    swatch_count = 0
    sort_type = None
    wait = 0

    def __init__(self, options):
        if options.file is None:
            clipboard = pyperclip.paste().strip('"')
            if '.csv' in clipboard.lower():
                self.csv_file = clipboard
            else:
                self.mode = 'clipboard'
        else:
            self.csv_file = options.file
        self.sort_type = options.sort
        self.wait = options.wait


    def get_swatches_from_data(self, data, html=False):
        """Retrieves swatch values from data"""

        if html is False:
            # Treat CSV data as dictionary
            reader = csv.DictReader(data)

            # Grab that data!
            for row in reader:
                # Formatting differs between Pro and Mini sensors
                try:  # Mini
                    hex_value = row[' HEX'].replace(' ', '')
                    rgb_value = (
                        int(row[' sRGB R']),
                        int(row[' sRGB G']),
                        int(row[' sRGB B'])
                    )
                except KeyError:  # Pro
                    hex_value = row['HEX']
                    try:
                        rgb_value = (
                            int(row['R']),
                            int(row['G']),
                            int(row['B'])
                        )
                    except TypeError:
                        rgb_value = (0, 0, 0)

                # Add a swatch to list if there is data
                if hex_value != '' and rgb_value != (0, 0, 0):
                    self.swatches.append(Swatch(hex_value, rgb_value))
        else:
            for word in data.split():
                if 'color=#' in word:
                    hex_value = word.split('=')[1]  # grab HEX value after '='
                    red, green, blue = bytes.fromhex(hex_value[1:])  # skip '#' char
                    rgb_value = (red, green, blue)
                    self.swatches.append(Swatch(hex_value, rgb_value))


    def get_swatches(self):
        """Provides data to get_swatches_from_data"""

        # Get swatches from clipboard or CSV file
        if self.mode == 'clipboard':
            messager('status_clipboard')

            clipboard_data = pyperclip.paste()

            if 'HEX,' in clipboard_data:  # simple check for valid CSV data
                self.get_swatches_from_data(clipboard_data.splitlines())
                # splitlines() only works here? ^ wut o_O
            elif '<font color=#' in clipboard_data:  # must be our own HTML output
                messager('status_html')
                self.get_swatches_from_data(clipboard_data, html=True)
            else:
                messager(
                    ['error_clipboard_nodata', 'info_tryhelp'],
                    exit_after=True, wait=self.wait
                )
        else:
            if self.csv_file is not None:
                messager('status_file', self.csv_file)
                with open(self.csv_file) as f:
                    self.get_swatches_from_data(f)
            else:
                messager(
                    ['error_nodata', 'info_tryhelp'],
                    exit_after=True, wait=self.wait
                )


    def sort_swatches(self):
        """Sort swatches by hue, saturation, or value."""

        if self.sort_type is None:
            return

        sort_type = self.sort_type.lower()

        if 'hue' in sort_type:
            self.swatches = sorted(
                self.swatches,
                key=lambda x: (colorsys.rgb_to_hsv(
                    x.rgb_value[0], x.rgb_value[1], x.rgb_value[2])[0])
            )
        elif 'sat' in sort_type:
            self.swatches = sorted(
                self.swatches,
                key=lambda x: (colorsys.rgb_to_hsv(
                    x.rgb_value[0], x.rgb_value[1], x.rgb_value[2])[1])
            )
        elif 'val' in sort_type:
            self.swatches = sorted(
                self.swatches,
                key=lambda x: (colorsys.rgb_to_hsv(
                    x.rgb_value[0], x.rgb_value[1], x.rgb_value[2])[2])
            )
        else:
            messager(['error_sort', 'info_tryhelp'], extra_info=sort_type,
                     exit_after=True, wait=self.wait)


    def output_swatches(self):
        """ Output swatches to console and clipboard. """

        output = ''
        for swatch in self.swatches:
            swatch.print()
            output += swatch.html

        pyperclip.copy(output)


def main():
    """
    MAIN
    """
    arg_parser = argparse.ArgumentParser(
        description='\n'.join(__doc__.splitlines()[0:4]),
        epilog=__doc__.splitlines()[-1]
    )
    arg_parser.add_argument(
        '-f', '--file', metavar='NAME',
        help='use data from CSV file: NAME'
    )
    arg_parser.add_argument(
        '-s', '--sort', metavar='TYPE',
        help='sort swatches by TYPE(hue, sat, val)'
    )
    arg_parser.add_argument(
        '-w', '--wait', metavar='N', type=int, default=0,
        help='wait N seconds before exiting'
    )
    arg_parser.add_argument(
        '-v', '--version', action='version', version='version: %s' % VERSION
    )

    print() # Blank line for formatting

    options = arg_parser.parse_args()

    csv_parser = CSVParser(options)
    csv_parser.get_swatches()
    csv_parser.sort_swatches()
    csv_parser.output_swatches()

    # Report.
    count = len(csv_parser.swatches)
    if csv_parser.sort_type is not None:
        print(
            '\n...%i HTML swatches sorted by %s copied to the clipboard!\n' % (
                count, csv_parser.sort_type.upper()
            )
        )
    else:
        print('\n...%i HTML swatches copied to clipboard!\n' % count)

    exit_wait(csv_parser.wait)


if __name__ == '__main__':
    main()
