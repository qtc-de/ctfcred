#!/usr/bin/python3

import pyotp
import pytest
import ctfcred
import pyperclip

from ctfcred.launcher import Launcher


@pytest.mark.usefixtures('cred')
def test_overwrite_launcher(cred):
    '''
    Dirty way to prevent other windows to popup during tests.

    Parameters:
        cred            Dummy credential object

    Returns:
        None
    '''
    Launcher.start_rofi = lambda *args: [99, cred]
    Launcher.notify_send = lambda *args: None


@pytest.mark.usefixtures('cred_list')
def test_delete(cred_list):
    '''
    Test whether delete operation is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    cred = cred_list[2]
    initial_len = len(cred_list)

    with pytest.raises(ctfcred.launcher.RofiException, match="rofi returned unexpected return code: 99"):
        Launcher.handle_exit(12, cred, cred_list)

    assert len(cred_list) == initial_len - 1
    assert cred not in cred_list


@pytest.mark.usefixtures('cred_list')
def test_password_copy(cred_list):
    '''
    Test whether copying passwords is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    for cred in cred_list:

        Launcher.handle_exit(0, cred, cred_list)
        copied_password = pyperclip.paste()

        assert copied_password == cred.password or 'None'

        Launcher.handle_exit(10, cred, cred_list)
        copied_password = pyperclip.paste()

        assert copied_password == cred.password or 'None'


@pytest.mark.usefixtures('cred_list')
def test_username_copy(cred_list):
    '''
    Test whether copying usernames is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    for cred in cred_list:

        Launcher.handle_exit(11, cred, cred_list)
        copied_username = pyperclip.paste()

        assert copied_username == cred.username or 'None'


@pytest.mark.usefixtures('cred_list')
def test_otp_copy(cred_list):
    '''
    Test whether copying otp codes is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    for cred in cred_list:

        Launcher.handle_exit(13, cred, cred_list)
        copied_otp = pyperclip.paste()

        if cred.otp:
            compare = pyotp.TOTP(cred.otp).now()
        else:
            compare = 'None'

        assert copied_otp == compare


@pytest.mark.usefixtures('cred_list')
def test_url_copy(cred_list):
    '''
    Test whether copying url is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    for cred in cred_list:

        Launcher.handle_exit(14, cred, cred_list)
        copied_url = pyperclip.paste()

        assert copied_url == cred.url or 'None'


@pytest.mark.usefixtures('cred_list')
def test_default_url_copy(cred_list):
    '''
    Test whether copying url with default is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    default_url = 'https://default.org'
    ctfcred.config.Config.default_url = default_url

    for cred in cred_list:

        Launcher.handle_exit(14, cred, cred_list)
        copied_url = pyperclip.paste()

        assert copied_url == cred.url or default_url

    ctfcred.config.Config.default_url = None


@pytest.mark.usefixtures('cred_list')
def test_domain_copy(cred_list):
    '''
    Test whether copying domains is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    for cred in cred_list:

        Launcher.handle_exit(15, cred, cred_list)
        copied_domain = pyperclip.paste()

        assert copied_domain == cred.domain or 'None'


@pytest.mark.usefixtures('cred_list')
def test_default_domain_copy(cred_list):
    '''
    Test whether copying domains with default is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    default_domain = 'default.org'
    ctfcred.config.Config.default_domain = default_domain

    for cred in cred_list:

        Launcher.handle_exit(15, cred, cred_list)
        copied_domain = pyperclip.paste()

        assert copied_domain == cred.domain or default_domain

    ctfcred.config.Config.default_domain = None


@pytest.mark.usefixtures('cred_list')
def test_user_domain_copy(cred_list):
    '''
    Test whether copying usernames with domain is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    for cred in cred_list:

        Launcher.handle_exit(16, cred, cred_list)
        copied_user_domain = pyperclip.paste()

        if cred.domain:
            compare = f'{cred.domain}/{cred.username}'
        else:
            compare = cred.username or 'None'

        assert copied_user_domain == compare


@pytest.mark.usefixtures('cred_list')
def test_default_user_domain_copy(cred_list):
    '''
    Test whether copying users with domain and default is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    default_domain = 'default.org'
    ctfcred.config.Config.default_domain = default_domain

    for cred in cred_list:

        Launcher.handle_exit(16, cred, cred_list)
        copied_user_domain = pyperclip.paste()

        if cred.domain:
            compare = f'{cred.domain}/{cred.username}'
        else:
            compare = f'{default_domain}/{cred.username}'

        assert copied_user_domain == compare


@pytest.mark.usefixtures('cred_list')
def test_move_up(cred_list):
    '''
    Test whether moving credentials is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    cred0 = cred_list[0]
    cred1 = cred_list[1]
    cred0_id = cred0.id
    cred1_id = cred1.id

    with pytest.raises(ctfcred.launcher.RofiException, match="rofi returned unexpected return code: 99"):
        Launcher.handle_exit(17, cred1, cred_list)

    assert cred0_id == cred_list[1].id
    assert cred1_id == cred_list[0].id


@pytest.mark.usefixtures('cred_list')
def test_move_down(cred_list):
    '''
    Test whether moving credentials is working.

    Parameters:
        cred_list       List of credential objects

    Returns:
        None
    '''
    cred0 = cred_list[0]
    cred1 = cred_list[1]
    cred0_id = cred0.id
    cred1_id = cred1.id

    with pytest.raises(ctfcred.launcher.RofiException, match="rofi returned unexpected return code: 99"):
        Launcher.handle_exit(18, cred0, cred_list)

    assert cred0_id == cred_list[1].id
    assert cred1_id == cred_list[0].id
