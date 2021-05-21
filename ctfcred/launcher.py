from __future__ import annotations

import pyotp
import pyperclip
import subprocess

from typing import Any
from ctfcred.config import Config
from ctfcred.credential import Credential


class RofiException(Exception):
    '''
    Custom Exception class.
    '''


class Launcher:
    '''
    This class is responsible for laucnhing external programs.
    '''

    def notify_send(item: Any, msg: str = None) -> None:
        '''
        Send a user notification using notify-send command. By default, the message contains
        information that a certain item was copied.

        Parameters:
            item        Item that was copied to clipboard
            msg         Alternative message to send

        Returns:
            None
        '''
        if msg is not None:
            message = msg

        else:
            message = '{} copied to clipboard'.format(item or 'None')

        if Config.notify_send:
            subprocess.call(['notify-send', '-t', '1500', message])

    def copy_otp(secret: str) -> None:
        '''
        Generate and copy an OTP to the clipboard.

        Parameters:
            secret          Base32 encoded secret

        Returns:
            None
        '''
        if secret is not None:
            otp = pyotp.TOTP(secret).now()
            pyperclip.copy(otp)
            Launcher.notify_send(otp)

        else:
            Launcher.copy_wrapper(None)

    def copy_wrapper(item: str) -> None:
        '''
        Copies the specified item to the clipboard. If the item is None,
        copy 'None' to the clipboard.

        Parameters:
            item        Item to copy to the clipboard

        Returns:
            None
        '''
        if item is not None:
            pyperclip.copy(item)
            Launcher.notify_send(item)

        else:
            pyperclip.copy('None')
            Launcher.notify_send('None')

    def copy_default(item: str, type_str: str) -> None:
        '''
        If item exists, copy it to clipboard. Otherwise, copy the default
        value to clipboard.

        Parameters:
            item        Item to copy to the clipboard
            type_str    Either url or domain

        Returns:
            None
        '''
        if item:
            Launcher.copy_wrapper(item)

        elif type_str == 'url':
            Launcher.copy_wrapper(Config.default_url)

        elif type_str == 'domain':
            Launcher.copy_wrapper(Config.default_domain)

        else:
            Launcher.copy_wrapper('None')

    def copy_user_domain(cred: Credential) -> None:
        '''
        Copy a user with it's corresponding domain or the default domain.

        Parameters:
            cred        Credential that represents the user

        Returns:
            None
        '''
        if cred.domain:
            Launcher.copy_wrapper(f'{cred.domain}/{cred.username}')

        elif Config.default_domain:
            Launcher.copy_wrapper(f'{Config.default_domain}/{cred.username}')

        else:
            Launcher.copy_wrapper(cred.username)

    def open_url(cred: Credential) -> None:
        '''
        Open the url specified within the credential with the defaultn browser.

        Parameters:
            cred        Credential containing the desired URL

        Returns:
            None
        '''
        if not Config.browser or not cred.url:
            return

        subprocess.call(['xdg-open', cred.url])

    def start_rofi(credentials: set[Credential], prompt: str = 'Select Credential') -> tuple[int, Credential]:
        '''
        Takes a set of credential objects and displays them within rofi. Retruns the selected
        credential object and the exit code of rofi.

        Parameters:
            credentials         Set of credential objects to display

        Returns:
            Credential          User selected credential
        '''
        command = ['rofi', '-dmenu', '-format', 'i', '-p', prompt] + Config.key_mappings
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        cred_list = sorted(credentials, key=lambda x: x.id)

        for cred in cred_list:
            process.stdin.write(cred.format().encode('utf-8'))

        try:
            index = (process.communicate()[0]).decode('utf-8')
            index = int(index)

        except ValueError:
            raise RofiException(f"rofi returned unexpected index: '{index}'.")

        credential = cred_list[index]
        return (process.returncode, credential)

    def handle_exit(code: int, cred: Credential, cred_list: list[Credential]) -> None:
        '''
        Performs an action accordin to the exit code of rofi.

        Parameters:
            code            Exit code of rofi
            cred            User selected credential object
            cred_list       List of all available credentials

        Returns:
            None
        '''
        if Launcher.handle_copy(code, cred):
            pass

        elif Launcher.handle_movement(code, cred, cred_list):
            pass

        elif code == 12:
            cred_list.remove(cred)

            Credential.to_file(cred_list)
            creds = Credential.from_file()

            status, selected = Launcher.start_rofi(creds)
            Launcher.handle_exit(status, selected, creds)

        elif code == 19:
            Launcher.open_url(cred)

        else:
            raise RofiException(f'rofi returned unexpected return code: {code}.')

    def handle_movement(code: int, cred: Credential, cred_list: set[Credential]) -> bool:
        '''
        Handle credential movement according to rofi status code.

        Parameters:
            code            Rofi status code
            cred            Selected credential object
            cred_list       Credential list

        Returns:
            bool            True if movement code, false otherwise
        '''
        old_id = cred.id

        if code == 17:
            new_id = cred.id - 1

        elif code == 18:
            new_id = cred.id + 1

        else:
            return False

        other = Credential.get_by_id(new_id, cred_list)

        if other:

            other.id = old_id
            cred.id = new_id

            Credential.to_file(cred_list)
            creds = Credential.from_file()

            status, selected = Launcher.start_rofi(creds)
            Launcher.handle_exit(status, selected, creds)

        return True

    def handle_copy(code: int, cred: Credential) -> bool:
        '''
        Handle credential copy operations according to rofi status code.

        Parameters:
            code            Rofi status code
            cred            Selected credential object

        Returns:
            bool            True if copy code, false otherwise
        '''
        if code == 0 or code == 10:
            Launcher.copy_wrapper(cred.password)

        elif code == 11:
            Launcher.copy_wrapper(cred.username)

        elif code == 13:
            Launcher.copy_otp(cred.otp)

        elif code == 14:
            Launcher.copy_default(cred.url, 'url')

        elif code == 15:
            Launcher.copy_default(cred.domain, 'domain')

        elif code == 16:
            Launcher.copy_user_domain(cred)

        else:
            return False

        return True
