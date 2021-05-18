#!/usr/bin/env python3

from __future__ import annotations

from typing import Union


def print_collection(col: Union[list, set]):
    '''
    Prints each item of the specified collection.

    Parameters:
        col         Collection type to print

    Returns:
        None
    '''
    for item in col:
        print(item)
