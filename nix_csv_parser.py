#!/usr/bin/env python3
# encoding: utf-8
# by Will Fuller, sinistergfx@gmail.com

"""
Usage:
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

VERSION = '1.0.2 (2017.10.03)'
SWATCH_CHAR = '▄'
SWATCH_SIZE = '72px'


class Swatch():
    """
    Holds swatch data
    """
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
        """ Set swatch output html """
        self.html = (
            '<font color=%s size=%s>%s </font>'
            '<b>HEX:</b> %s - <b>RGB:</b> %s<br>\n' % (
                self.hex_value, SWATCH_SIZE, SWATCH_CHAR,
                self.hex_value, str(self.rgb_value)
            )
        )


    def print(self):
        """ Output swatch data to console """
        print('  %s HEX: %s - RGB: %s' % (
                SWATCH_CHAR,
                self.hex_value,
                self.rgb_value
            )
        )



def exit_wait(wait=0):
    """
    Optionally wait before exiting
    """
    time.sleep(wait)
    exit()


def exit_info(info, wait=0):
    """
    Displays information and exits
    """

    if info == 'help':
        print(__doc__)
    elif info == 'usage':
        # Print 'usage' from docstring
        print('\n'.join(__doc__.splitlines()[0:4]))
        exit_info('try_help', wait)
    elif info == 'version':
        print('version: %s\n' % VERSION)
    elif info == 'try_help':
        print("Try 'nix_csv_parser.py --help' for more information\n")

    exit_wait(wait)


def parse_args():
    """
    Parses arguments/options
    Returns: csv_file, sort_type, mode, wait
    """
    # Set return defaults
    csv_file = None
    sort_type = None
    mode = 'file'
    wait = 0

    # Grab arguments if there are any
    if len(sys.argv) > 1:
        args = [str(arg) for arg in sys.argv[1:]]

        # Determine wait value if specified
        for i, arg in enumerate(args):
            if (arg[0] == '-' and arg[-1] == 'w') or arg == '--wait':
                # Next arg should be wait value
                if len(args) > i+1 and args[i+1].isdigit():
                    wait = int(args[i+1])

                    # Keep wait value from showing up in options
                    del args[i+1]

                    # Done with wait args, might as well remove them
                    if arg == '--wait':
                        del args[i]
                    else:
                        args[i] = arg.strip('w')

                    break
                else:
                    print('\nError - Invalid/missing wait value.\n')
                    exit_info('try_help', 1)

        # Generate options list and grab CSV file

        options = []
        csv_file = None
        for arg in args:
            if arg[0:2] == '--':  # long name options
                options.append(arg[2:])
            elif arg[0] == '-':  # single letter options, may be combined
                options.extend(list(arg[1:]))
            elif '.csv' in arg.lower():  # CSV file
                csv_file = arg

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

                print("\nError - Unrecognized option: '%s%s'\n" % (
                    prefix, option))
                exit_info('try_help', wait)

        # Information display options
        if 'H' in options or 'help' in options:
            exit_info('help', wait)
        elif 'V' in options or 'version' in options:
            exit_info('version', wait)

        # Determine file/clipboard mode
        if 'c' in options or 'clipboard' in options:
            clipboard_data = pyperclip.paste()
            # Detect if file path is in clipboard
            if '.csv' in clipboard_data.lower():
                csv_file = clipboard_data.strip('"')  # Strip " because Windows
            else:  # Assume data is in clipboard, switch mode
                mode = 'clipboard'

        # Determine sort type
        if 'h' in options or 'sort-hue' in options:
            sort_type = 'hue'
        elif 's' in options or 'sort-sat' in options:
            sort_type = 'saturation'
        elif 'v' in options or 'sort-val' in options:
            sort_type = 'value'

    else:  # Abort if no arguments given
        exit_info('usage')

    return(csv_file, sort_type, mode, wait)


def get_swatches(data):
    """
    Returns list of HEX and RGB swatch data from Nix CSV data
    """
    swatches = []

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
            swatches.append((hex_value, rgb_value))

    return swatches


def get_swatches_html(html):
    """
    Gets swatches from our own html data, so we don't have to re-copy
        from CSV data to re-sort
    """
    swatches = []

    for word in html.split():
        if 'color=#' in word:
            hex_value = word.split('=')[1]  # grab HEX value after '='
            red, green, blue = bytes.fromhex(hex_value[1:])  # skip '#' char
            rgb_value = (red, green, blue)
            swatches.append((hex_value, rgb_value))

    return swatches


def sort_swatches(swatches, sort_type):
    """
    Sorts swatches by hue, saturation, or value
    """
    if sort_type == 'hue':
        swatches = sorted(
            swatches,
            key=lambda x: (colorsys.rgb_to_hsv(x[1][0], x[1][1], x[1][2])[0])
        )
    elif sort_type == 'saturation':
        swatches = sorted(
            swatches,
            key=lambda x: (colorsys.rgb_to_hsv(x[1][0], x[1][1], x[1][2])[1])
        )
    elif sort_type == 'value':
        swatches = sorted(
            swatches,
            key=lambda x: (colorsys.rgb_to_hsv(x[1][0], x[1][1], x[1][2])[2])
        )

    return swatches


def output_swatches(swatches, swatch_size, swatch_char):
    """
    Builds HTML output from swatches and copies to clipboard
    """
    output = ''

    for swatch in swatches:
        hex_value = swatch[0]
        rgb_value = swatch[1]

        print('  %s HEX: %s - RGB: %s' % (swatch_char, hex_value, rgb_value))

        # Create HTML swatches
        line = (
            '<font color=%s size=%s>%s </font>'
            '<b>HEX:</b> %s - <b>RGB:</b> %s<br>\n' % (
                hex_value, swatch_size,	swatch_char,
                hex_value, str(rgb_value)
            )
        )
        output += line

    # Output to clipboard
    pyperclip.copy(output)


def main():
    """
    MAIN
    """
    # Set options from arguments
    csv_file, sort_type, mode, wait = parse_args()

    print()

    # Get swatches from clipboard or CSV file
    if mode == 'clipboard':
        print('Reading CSV data from clipboard...\n')

        clipboard_data = pyperclip.paste()

        if 'HEX,' in clipboard_data:  # simple check for valid CSV data
            swatches = get_swatches(clipboard_data.splitlines())
            # splitlines() only works here? ^ wut o_O
        elif '<font color=#' in clipboard_data:  # must be our own HTML output
            print('HTML data found instead, no problem...\n')
            swatches = get_swatches_html(clipboard_data)
        else:
            print('Error - No CSV data found in clipboard.\n')
            exit_info('try_help', wait)
    else:
        if csv_file is not None:
            print('Reading CSV data from %s...\n' % csv_file)
            with open(csv_file) as file:
                swatches = get_swatches(file)
        else:
            print('Error - No CSV data provided.')
            exit_info('usage', wait)

    # HSV Sorting
    if sort_type is not None:
        swatches = sort_swatches(swatches, sort_type)

    # Build HTML output and copy to clipboard
    output_swatches(swatches, SWATCH_SIZE, SWATCH_CHAR)

    # Report.
    count = len(swatches)
    if sort_type is not None:
        print(
            '\n...%i HTML swatches sorted by %s '
            'copied to the clipboard!\n' % (
                count, sort_type.upper()
            )
        )
    else:
        print('\n...%i HTML swatches copied to clipboard!\n' % count)

    exit_wait(wait)


if __name__ == '__main__':
    main()
