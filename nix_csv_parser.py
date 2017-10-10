#!/usr/bin/env python3
# encoding: utf-8
# by Will Fuller, sinistergfx@gmail.com

"""Usage:
    nix_csv_parser.py [CSV filename] [options]

Parses Nix Color Sensor CSV data, outputs HTML-based swatches to clipboard.
Optionally sort output by hue, saturation, or value.

Options:
    Single letter options may be combined. ex: '-cvw 2'

    -c, --clipboard     : Use CSV data or file path from clipboard

    -h, --sort-hue      : Sort swatches by hue
    -s, --sort-sat      : Sort swatches by saturation
    -v, --sort-val      : Sort swatches by value

    -w #, --wait #      : Wait # seconds before exit
                          (must be last in group if combining)

    -H, --help          : Show this help message
    -V, --version       : Show version

Example usage:
    $ nix_csv_parser.py somefile.csv
        (unsorted output from CSV file)
    $ nix_csv_parser.py somefile.csv --sort-value --wait 3
        (value sorted output from CSV file, wait 3 seconds)
    $ nix_csv_parser.py -cs
        (saturation sorted output from clipboard)
    $ nix_csv_parser.py -chw 5
        (hue sorted output from clipboard, wait 5 seconds)

Created by Will Fuller, sinistergfx@gmail.com
"""

import sys
import time
import csv
import colorsys

import pyperclip

VERSION = '1.1.1 (2017.10.09)'
SWATCH_CHAR = '▄'
SWATCH_SIZE = '72px'


def exit_wait(wait=0):
    """Optionally wait N seconds before exiting"""

    time.sleep(wait)
    exit()


def msg_display(msg, extra_info='', exit_after=False, wait=0):
    """Central message handling, optionally exit after display"""

    messages = {
        'error_clipboard_nodata':
            '! Error - No CSV data found in clipboard.\n',
        'error_nodata':
            '! Error - No CSV data provided.',
        'error_option':
            "! Error - Unrecognized option: '%s'\n" % extra_info,
        'error_wait':
            '! Error - Invalid/missing wait value.\n',
        'info_help':
            __doc__,
        'info_tryhelp':
            "Try 'nix_csv_parser.py --help' for more information\n",
        'info_usage':
            '\n'.join(__doc__.splitlines()[0:3]),
        'info_version':
            'version: %s\n' % VERSION,
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
    sort_type = None
    wait = 0

    def __init__(self):
        self.parse_args()


    def parse_args(self):
        """Parse command line arguments and set options"""

        if len(sys.argv) <= 1:
            # Abort if no arguments
            msg_display('info_usage', exit_after=True, wait=1)
        else:
            args = [str(arg) for arg in sys.argv[1:]]

            # Determine wait value
            for i, arg in enumerate(args):
                if (arg[0] == '-' and arg[-1] == 'w') or arg == '--wait':
                    # Next arg should be wait value
                    if len(args) > i+1 and args[i+1].isdigit():
                        self.wait = int(args[i+1])

                        # Keep wait value from showing up in options
                        del args[i+1]

                        # Done with wait args, might as well remove them
                        if arg == '--wait':
                            del args[i]
                        else:
                            args[i] = arg.strip('w')

                        break
                    # Next arg is missing or isn't an integer, error out
                    else:
                        msg_display(
                            ['error_wait', 'info_tryhelp'],
                            exit_after=True, wait=1
                        )

            # Generate options list and grab CSV file
            options = []
            for arg in args:
                if arg[0:2] == '--':  # long name options
                    options.append(arg[2:])
                elif arg[0] == '-':  # single letter options, may be combined
                    options.extend(list(arg[1:]))
                elif '.csv' in arg.lower():  # CSV file
                    self.csv_file = arg

            # Error out for invalid options.
            possible_options = (
                'H', 'help', 'V', 'version', 'c', 'clipboard',
                'h', 'sort-hue', 's', 'sort-sat', 'v', 'sort-val')
            for option in options:
                if option not in possible_options:
                    if len(option) > 1:
                        prefix = '--'
                    else:
                        prefix = '-'

                    msg_display(
                        ['error_option', 'info_tryhelp'],
                        extra_info=prefix+option,
                        exit_after=True,
                        wait=self.wait)

            # Information display options
            if 'H' in options or 'help' in options:
                msg_display('info_help', exit_after=True, wait=self.wait)
            elif 'V' in options or 'version' in options:
                msg_display('info_version', exit_after=True, wait=self.wait)

            # Determine file/clipboard mode
            if 'c' in options or 'clipboard' in options:
                clipboard_data = pyperclip.paste()
                # Detect if file path is in clipboard
                if '.csv' in clipboard_data.lower():
                    self.file = clipboard_data.strip('"')  # because: Windows
                else:  # Assume data is in clipboard, switch mode
                    self.mode = 'clipboard'

            # Determine sort type
            if 'h' in options or 'sort-hue' in options:
                self.sort_type = 'hue'
            elif 's' in options or 'sort-sat' in options:
                self.sort_type = 'saturation'
            elif 'v' in options or 'sort-val' in options:
                self.sort_type = 'value'



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
            msg_display('status_clipboard')

            clipboard_data = pyperclip.paste()

            if 'HEX,' in clipboard_data:  # simple check for valid CSV data
                self.get_swatches_from_data(clipboard_data.splitlines())
                # splitlines() only works here? ^ wut o_O
            elif '<font color=#' in clipboard_data:  # must be our own HTML output
                msg_display('status_html')
                self.get_swatches_from_data(clipboard_data, html=True)
            else:
                msg_display(
                    ['error_clipboard_nodata', 'info_tryhelp'],
                    exit_after=True, wait=self.wait
                )
        else:
            if self.csv_file is not None:
                msg_display('status_file', extra_info=self.csv_file)
                with open(self.csv_file) as f:
                    self.get_swatches_from_data(f)
            else:
                msg_display(
                    ['error_nodata', 'info_usage', 'info_tryhelp'],
                    exit_after=True, wait=self.wait
                )


    def sort_swatches(self):
        """Sort swatches by hue, saturation, or value."""

        if self.sort_type is None:
            return

        if self.sort_type == 'hue':
            self.swatches = sorted(
                self.swatches,
                key=lambda x: (colorsys.rgb_to_hsv(
                    x.rgb_value[0], x.rgb_value[1], x.rgb_value[2])[0])
            )
        elif self.sort_type == 'saturation':
            self.swatches = sorted(
                self.swatches,
                key=lambda x: (colorsys.rgb_to_hsv(
                    x.rgb_value[0], x.rgb_value[1], x.rgb_value[2])[1])
            )
        elif self.sort_type == 'value':
            self.swatches = sorted(
                self.swatches,
                key=lambda x: (colorsys.rgb_to_hsv(
                    x.rgb_value[0], x.rgb_value[1], x.rgb_value[2])[2])
            )


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

    print() # Blank line for formatting

    csv_parser = CSVParser()
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
