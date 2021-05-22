#!/usr/bin/env python3

import pytest
import ctfcred
import pyperclip


@pytest.fixture
def cred():
    '''
    Returns a single Credential object.

    Parameters:
        None

    Returns:
        obj             Single credential object
    '''
    ctfcred.Credential.reset_count()
    return ctfcred.Credential('tony', 'tonyPassword', 'this is tony', 'https://example.com', 'otpo', 'exmaple.com', 0, None)


@pytest.fixture
def cred_list():
    '''
    Returns a list of Credential objects.

    Parameters:
        None

    Returns:
        list            List of Credential objects
    '''
    ctfcred.Credential.reset_count()

    cred1 = ctfcred.Credential('timmy', 'password123', 'this is timmy', None, None, None, 0, None)
    cred2 = ctfcred.Credential('tony', 'tonyPassword', 'this is tony', 'https://example.com', 'otpo', 'exmaple.com', 0, None)
    cred3 = ctfcred.Credential('dummy', None, None, None, None, None, 0, None)
    cred4 = ctfcred.Credential('', 'lonelypassword', None, None, None, None, 0, None)

    return [cred1, cred2, cred3, cred4]


def pytest_addoption(parser):
    '''
    Not sure how to run clipboard tests in a CI properly. Until a better solution
    is available, we add an option for running in CI mode and mock clipboard calls
    in this case.
    '''
    parser.addoption("--ci-mode", action="store_true")


def pytest_collection_modifyitems(config, items):
    '''
    Create mock functions for clipboard usages if in ci-mode.
    '''
    if not config.getoption('--ci-mode'):
        return

    def mock_copy(content):
        '''
        Mock function for copy calls.
        '''
        pyperclip.current_clipboard_content = content

    def mock_paste():
        '''
        Mock function for paste calls.
        '''
        return pyperclip.current_clipboard_content

    pyperclip.copy = mock_copy
    pyperclip.paste = mock_paste
