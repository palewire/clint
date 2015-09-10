# -*- coding: utf-8 -*-

"""
clint.textui.formatters
~~~~~~~~~~~~~~~~~~~~~~~

Core TextUI functionality for text formatting.

"""

from __future__ import absolute_import
from contextlib import contextmanager

from .colored import ColoredString, clean
from ..utils import tsplit, schunk


NEWLINES = ('\n', '\r', '\r\n')
MAX_WIDTHS = []


def min_width(string, cols, padding=' '):
    """Returns given string with right padding."""

    is_color = isinstance(string, ColoredString)

    stack = tsplit(str(string), NEWLINES)

    for i, substring in enumerate(stack):
        _sub = clean(substring).ljust((cols + 0), padding)
        if is_color:
            _sub = (_sub.replace(clean(substring), substring))
        stack[i] = _sub
        
    return '\n'.join(stack)


def _get_max_width_context():
    return MAX_WIDTHS

@contextmanager
def _max_width_context():
    """Max width context manager."""
    try:
        yield
    finally:
        MAX_WIDTHS.pop()

def max_width(*args, **kwargs):
    """Returns formatted text or context manager for textui:puts.

        >>> from clint.textui import puts, max_width
        >>> max_width('123 5678', 8)
        '123 5678'
        >>> max_width('123 5678', 7)
        '123 \n5678'
        >>> with max_width(7):
        ...     puts('123 5678')
        '123 \n5678'
    """
    args = list(args)

    if not args:
        args.append(kwargs.get('string'))
        args.append(kwargs.get('cols'))
        args.append(kwargs.get('separator'))
    elif len(args) == 1:
        args.append(kwargs.get('cols'))
        args.append(kwargs.get('separator'))
    elif len(args) == 2:
        args.append(kwargs.get('separator'))

    string, cols, separator = args
    if separator is None:
        separator = '\n'  # default value
    if cols is None:
        # cols should be specified vitally
        # because string can be specified at textui:puts function
        string, cols = cols, string

    if string is None:
        MAX_WIDTHS.append((cols, separator))
        return _max_width_context()
    else:
        return _max_width_formatter(string, cols, separator)


def _max_width_formatter(string, cols, separator='\n'):
    """Returns a freshly formatted
    :param string: string to be formatted
    :type string: basestring or clint.textui.colorred.ColoredString
    :param cols: max width the text to be formatted
    :type cols: int
    :param separator: separator to break rows
    :type separator: basestring
    """

    is_color = isinstance(string, ColoredString)

    if is_color:
        string_copy = string._new('')
        string = string.s

    stack = tsplit(string, NEWLINES)

    for i, substring in enumerate(stack):
        stack[i] = substring.split()

    _stack = []
    
    for row in stack:
        _row = ['',]
        _row_i = 0

        for word in row:
            if (len(_row[_row_i]) + len(word)) <= cols:
                _row[_row_i] += word
                _row[_row_i] += ' '
                
            elif len(word) > cols:

                # ensure empty row
                if len(_row[_row_i]):
                    _row[_row_i] = _row[_row_i].rstrip()
                    _row.append('')
                    _row_i += 1

                chunks = schunk(word, cols)
                for i, chunk in enumerate(chunks):
                    if not (i + 1) == len(chunks):
                        _row[_row_i] += chunk
                        _row[_row_i] = _row[_row_i].rstrip()
                        _row.append('')
                        _row_i += 1
                    else:
                        _row[_row_i] += chunk
                        _row[_row_i] += ' '
            else:
                _row[_row_i] = _row[_row_i].rstrip()
                _row.append('')
                _row_i += 1
                _row[_row_i] += word
                _row[_row_i] += ' '
        else:
            _row[_row_i] = _row[_row_i].rstrip()

        _row = map(str, _row)
        _stack.append(separator.join(_row))

    _s = '\n'.join(_stack)
    if is_color:
        _s = string_copy._new(_s)
    return _s
