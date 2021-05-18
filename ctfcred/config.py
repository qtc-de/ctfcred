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

    move_up = 'Ctrl+K'
    copy_otp = 'Ctrl+o'
    copy_url = 'Ctrl+l'
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
                    '-kb-custom-9', move_down
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

    def key_bindings() -> str:
        '''
        Returns a formatted string of the currently defined keybindings. This is used within
        the helptext for the tool.

        Parameters:
            None

        Returns:
            str         formatted list of Keybindings
        '''
        return_str = 'key bindings:\n'

        return_str += f'  {Config.copy_username}\t\tCopy Username\n'
        return_str += f'  {Config.copy_password}\t\tCopy Password\n'
        return_str += f'  {Config.copy_otp}\t\tCopy OTP Value\n'
        return_str += f'  {Config.copy_url}\t\tCopy URL Value\n'
        return_str += f'  {Config.copy_domain}\t\tCopy Domain\n'
        return_str += f'  {Config.copy_user_domain}\t\tCopy User with Domain\n'
        return_str += f'  {Config.delete_credential}\t\tDelete Credential\n'
        return_str += f'  {Config.move_up}\t\tMove Credential one Up\n'
        return_str += f'  {Config.move_down}\t\tMove Credential one Down\n'

        return return_str
