from __future__ import annotations

import yaml
import shutil

from pathlib import Path


class DependencyException(Exception):
    '''
    Custom Exception class.
    '''


class MalformedCredentialFile(Exception):
    '''
    Custom Exception class.
    '''


class Config:
    '''
    The Config class is used to store some configuration values and to perform
    checks for available helper programs on the machine.
    '''
    notify_send = True
    browser = True

    move_up = 'Ctrl+K'
    copy_otp = 'Ctrl+o'
    copy_url = 'Ctrl+l'
    open_url = 'Ctrl+L'
    move_down = 'Ctrl+J'
    copy_domain = 'Ctrl+D'
    copy_username = 'Ctrl+C'
    copy_password = 'Ctrl+c'
    copy_user_domain = 'Ctrl+F'
    delete_credential = 'Ctrl+X'

    key_mappings = [
                    '-kb-custom-1', copy_password,
                    '-kb-custom-2', copy_username,
                    '-kb-custom-3', delete_credential,
                    '-kb-custom-4', copy_otp,
                    '-kb-custom-5', copy_url,
                    '-kb-custom-6', copy_domain,
                    '-kb-custom-7', copy_user_domain,
                    '-kb-custom-8', move_up,
                    '-kb-custom-9', move_down,
                    '-kb-custom-10', open_url
                   ]

    url_sep = 30
    user_sep = 20

    credential_file = Path.home().joinpath('.ctfcred.yml')

    default_url = None
    default_domain = None

    def check_external_dependencies() -> None:
        '''
        Checks if the required external execuatbles are present.

        Parameters:
            None

        Returns:
            None
        '''
        if not shutil.which('rofi'):
            raise DependencyException("Unable to find 'rofi' in your current PATH.")

        if not shutil.which('notify-send'):
            Config.notify_send = False

        if not shutil.which('xdg-open'):
            Config.browser = False

    def parse_cred_file() -> dict:
        '''
        Parses the credential file and returns it's content as dict.

        Parameters:
            None

        Returns:
            content     content of the credential file
        '''
        if not Config.credential_file.is_file():
            Config.credential_file.touch()

        with open(Config.credential_file, 'r') as file:

            try:
                yml = yaml.safe_load(file)

            except yaml.YAMLError as e:
                raise MalformedCredentialFile(str(e))

        if yml:
            Config.default_url = Config.default_url or yml.get('default_url', None)
            Config.default_domain = Config.default_domain or yml.get('default_domain', None)

        return yml

    def write_cred_file(yml: dict) -> None:
        '''
        Writes the credential file using the specified dictionary. Apart from user
        credentials, appends the global default url and global default domain.

        Parameters:
            yml         dictionary that contains the credentials to write

        Returns:
            None
        '''
        yml['default_url'] = Config.default_url
        yml['default_domain'] = Config.default_domain

        with open(Config.credential_file, 'w') as file:
            yaml.dump(yml, file, default_flow_style=False)

    def key_bindings(width: int) -> str:
        '''
        Returns a formatted string of the currently defined keybindings. This is used within
        the helptext for the tool. The width parameter controlls the padding of the argument
        descriptions.

        Parameters:
            width       padding between key binding and description

        Returns:
            str         formatted list of Keybindings
        '''
        return_str = 'key bindings:\n'

        return_str += f'  {Config.copy_username.ljust(width)}Copy Username\n'
        return_str += f'  {Config.copy_password.ljust(width)}Copy Password\n'
        return_str += f'  {Config.copy_otp.ljust(width)}Copy OTP Value\n'
        return_str += f'  {Config.copy_url.ljust(width)}Copy URL Value\n'
        return_str += f'  {Config.open_url.ljust(width)}Open URL\n'
        return_str += f'  {Config.copy_domain.ljust(width)}Copy Domain\n'
        return_str += f'  {Config.copy_user_domain.ljust(width)}Copy User with Domain\n'
        return_str += f'  {Config.delete_credential.ljust(width)}Delete Credential\n'
        return_str += f'  {Config.move_up.ljust(width)}Move Credential one Up\n'
        return_str += f'  {Config.move_down.ljust(width)}Move Credential one Down\n\n'

        return return_str
