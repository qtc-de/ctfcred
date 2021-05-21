#!/usr/bin/env python3

import pytest
import ctfcred


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
