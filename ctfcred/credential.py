from __future__ import annotations

import time
import base64
import itertools

from pathlib import Path
from datetime import datetime
from ctfcred.config import Config
from ctfcred.utils import print_collection


class MissingCredentialAttribute(Exception):
    '''
    This exception is raised when the credential file misses an attribute on a credential
    This is usually the case when ctfcred was updated to a new version and an old credential
    file is attempted to be parsed.
    '''


class Credential:
    '''
    Credential objects represent one set of credentials and the corresponding
    associated items (username, password, url, otp, ...).
    '''
    count = itertools.count(1)

    def __init__(self, username: str, password: str, note: str, url: str, otp: str, domain: str,
                 created: int, c_note: bool = None, alias: str = None) -> None:
        '''
        Creates a new Credential object.

        Parameters:
            username        Username of the credential
            password        Password of the credential
            note            Additional note about the credential
            url             Related url
            otp             OTP base32 secret
            domain          Domain of the user
            created         Timestamp when the object was created
            c_note          Whether the specified note is a custom note
            alias           Alias to use for the username

        Returns:
            None
        '''
        self.id = next(self.count)
        self.timestamp = created or time.time()

        if note:
            self.note = note
            self.custom_note = True if c_note is None else c_note

        else:
            self.note = datetime.now()
            self.custom_note = False

        self.otp = otp
        self.url = url
        self.alias = alias
        self.username = username or None
        self.password = password or None
        self.domain = domain

    def __eq__(self, other: Credential) -> bool:
        '''
        Two Credential objects are equal, if they share excatly the same properties.

        Parameters:
            other           Credential object to compare to

        Returns:
            boolean         True or False
        '''
        if type(other) != Credential:
            return False

        retval = (self.username == other.username)
        retval = retval and (self.password == other.password)
        retval = retval and (self.otp == other.otp)
        retval = retval and (self.url == other.url)
        retval = retval and (self.domain == other.domain)

        if self.custom_note or other.custom_note:
            retval = retval and (self.note == other.note)

        return retval

    def __hash__(self) -> int:
        '''
        Computes the hash of a credential object that includes all attributes
        except it's id.

        Parameters:
            None

        Returns:
            hash         Hash value
        '''
        if self.custom_note:
            hash_tuple = (self.username, self.password, self.note, self.otp, self.url, self.domain)

        else:
            hash_tuple = (self.username, self.password, self.otp, self.url, self.domain)

        return hash(hash_tuple)

    def to_dict(self) -> dict:
        '''
        Transforms a credential object into it's dictionary representation.

        Parameters:
            None

        Returns:
            dict             Dict representation of a credential
        '''
        cred_dict = {
                     'username': self.username,
                     'password': self.password,
                     'otp': self.otp,
                     'note': self.note,
                     'custom_note': self.custom_note,
                     'url': self.url,
                     'domain': self.domain,
                     'timestamp': self.timestamp,
                     'alias': self.alias
                    }

        return cred_dict

    def get_hidden_property_string(self) -> str:
        '''
        Attributes like password, otp or domain are not displayed within rofi per default.
        This function returns a string that indicates which properties are available.

        Parameters:
            None

        Returns:
            prop_str            Property string (P=Password,O=TOP,D=Domain)
        '''
        prop_str = ''

        if self.password:
            prop_str += 'P'

        if self.otp:
            prop_str += 'O'

        if self.domain:
            prop_str += 'D'

        return prop_str.ljust(3)

    def format(self):
        '''
        Formats the credential object as it is displayed in rofi.

        Parameters:
            None

        Returns:
            None
        '''
        cid = f'{self.id}.'.ljust(4)

        if self.alias:
            username = Credential.ljust((self.alias), Config.user_sep)
        else:
            username = Credential.ljust((self.username or 'None'), Config.user_sep)

        url = Credential.ljust((self.url or ''), Config.url_sep)
        prop_str = self.get_hidden_property_string()
        note = self.note or ''
        return f'{cid}{username}{url}  {prop_str}  {note}\n'

    def clone(self, username: str, password: str, note: str, url: str, otp: str, domain: str, alias: str) -> Credential:
        '''
        Clones the current credential object.

        Parameters:
            username        New username
            password        New password
            note            New note
            url             New url
            otp             New otp
            domain          New domain
            alias           New alias

        Returns:
            credential      Cloned credential object
        '''
        username = username or self.username
        password = password or self.password
        url = url or self.url
        otp = otp or self.otp
        domain = domain or self.domain
        alias = alias or self.alias

        if note:
            note = note
            cnote = True

        else:
            note = self.note
            cnote = self.custom_note

        cred = Credential(username, password, note, url, otp, domain, 0, cnote, alias)
        return cred

    def update(self, username: str, password: str, note: str, url: str, otp: str, domain: str, alias: str) -> None:
        '''
        Update credential using the specified informations. If the specified
        parameters are None or empty, the old value is kept.

        Parameters:
            username        New username
            password        New password
            note            New note
            url             New url
            otp             New otp
            domain          New domain
            alias           New alias

        Returns:
            None
        '''
        self.username = username or self.username
        self.password = password or self.password
        self.url = url or self.url
        self.otp = otp or self.otp
        self.domain = domain or self.domain
        self.alias = alias or self.alias

        if note:
            self.note = note
            self.custom_note = True

    def from_file() -> set[Credential]:
        '''
        Retrieve a set of credentials from the credential file.

        Parameters:
            None

        Returns:
            credential      Set of Credential objects
        '''
        Credential.reset_count()

        credentials = set()
        yml = Config.parse_cred_file()

        if yml is None:
            return credentials

        try:

            for cred in yml.get('credentials', []):
                username = cred['username']
                password = cred['password']
                otp = cred['otp']
                note = cred['note']
                url = cred['url']
                domain = cred['domain']
                timestamp = cred['timestamp']
                c_note = cred['custom_note']
                alias = cred['alias']

                cred = Credential(username, password, note, url, otp, domain, timestamp, c_note, alias)
                credentials.add(cred)

        except KeyError as e:
            raise MissingCredentialAttribute(str(e))

        return credentials

    def to_file(credentials: set[Credential]) -> None:
        '''
        Takes a set of Credential objects and stores them to the credentials file.

        Parameters:
            credentials     Set of Credential objects

        Returns:
            None
        '''
        credentials = sorted(list(credentials), key=lambda x: x.id)
        credentials = list(map(lambda x: x.to_dict(), credentials))

        cred_dict = {'credentials': credentials}
        Config.write_cred_file(cred_dict)

    def export_usernames(credentials: set[Credential]) -> None:
        '''
        Exports usernames of all credentials into the specified file.

        Parameters:
            credentials     Set of Credential objects
            filename        File System path to copy to

        Returns:
            None
        '''
        usernames = list(map(lambda x: x.username, credentials))
        usernames = sorted(list(set(filter(lambda x: x, usernames))))
        print_collection(usernames)

    def export_passwords(credentials: set[Credential]) -> None:
        '''
        Exports passwords of all credentials into the specified file.

        Parameters:
            credentials     Set of Credential objects
            filename        File System path to copy to

        Returns:
            None
        '''
        passwords = list(map(lambda x: x.password, credentials))
        passwords = sorted(list(set(filter(lambda x: x, passwords))))
        print_collection(passwords)

    def export_domains(credentials: set[Credential]) -> None:
        '''
        Exports domains of all credentials into the specified file.

        Parameters:
            credentials     Set of Credential objects

        Returns:
            None
        '''
        domains = list(map(lambda x: x.domain, credentials))

        if Config.default_domain:
            domains.append(Config.default_domain)

        domains = sorted(list(set(filter(lambda x: x, domains))))
        print_collection(domains)

    def export_urls(credentials: set[Credential]) -> None:
        '''
        Exports urls of all credentials into the specified file.

        Parameters:
            credentials     Set of Credential objects

        Returns:
            None
        '''
        urls = list(map(lambda x: x.url, credentials))

        if Config.default_url:
            urls.append(Config.default_url)

        urls = sorted(list(set(filter(lambda x: x, urls))))
        print_collection(urls)

    def export_user_domain(credentials: set[Credential]) -> None:
        '''
        Exports usernames fixed with their domain prefix or the default domain.

        Parameters:
            credentials     Set of Credential objects

        Returns:
            None
        '''
        usernames = list()

        for cred in credentials:

            domain = cred.domain or Config.default_domain

            if domain:
                usernames.append(f'{domain}/{cred.username}')

            else:
                usernames.append(f'{cred.username}')

        usernames = sorted(list(set(usernames)))
        print_collection(usernames)

    def export_user_pass(credentials: set[Credential], sep: str, mix: bool, domain: bool, basic: bool) -> None:
        '''
        Export username:password combinations. If mix is set to true, each possible combination
        is exported.

        Parameters:
            credentials     Set of Credential objects
            sep             Separator to use between username and password
            mix             Export all possible username password combinations
            domain          Export usernames with domain
            basic           Export in basic-auth format

        Returns:
            None
        '''
        creds = set()

        if mix:
            pairs = itertools.product(credentials, credentials)

        else:
            pairs = [(i, i) for i in credentials]

        pairs = list(filter(lambda x: x[0].username and x[1].password, pairs))

        for cred, cred2 in pairs:

            domain_str = ''

            if domain:

                domain_str = cred.domain or Config.default_domain or ''

                if domain_str:
                    domain_str += '/'

            cred_str = f'{domain_str}{cred.username}{sep}{cred2.password}'
            creds.add(cred_str)

        creds = sorted(list(creds))

        if basic:
            creds = list(map(lambda x: base64.b64encode(x.encode('utf-8')).decode('utf-8'), creds))

        print_collection(creds)

    def import_usernames(filename: Path, with_domain: bool) -> set[Credential]:
        '''
        Import usernames from a file. If domain is true, slash characters are intrepreted as
        domain separator.

        Parameters:
            filename        Filename to import from
            with_domain     Use / as domain seprator

        Returns:
            creds           Set of credential objects
        '''
        creds = set()

        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:

            domain = None

            line = line.strip('\n')
            if '/' in line and with_domain:

                split = line.split('/')
                domain = split[0]
                line = '/'.join(split[1:])

            cred = Credential(line, None, 'Import', None, None, domain, 0)
            creds.add(cred)

        return creds

    def import_passwords(filename: Path) -> set[Credential]:
        '''
        Import passwords from a file.

        Parameters:
            filename        Filename to import from

        Returns:
            creds           Set of credential objects
        '''
        creds = set()

        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:

            line = line.strip('\n')
            cred = Credential(None, line, 'Import', None, None, None, 0)
            creds.add(cred)

        return creds

    def import_userpass(filename: Path, sep: str, with_domain: bool) -> set[Credential]:
        '''
        Import username password combinations from a file, separated by sep.

        Parameters:
            filename        Filename to import from
            sep             Separator to expect between username and password
            with_domain     Use / as domain seprator

        Returns:
            creds           Set of credential objects
        '''
        creds = set()

        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:

            line = line.strip('\n')
            domain = None

            if '/' in line and with_domain:

                split = line.split('/')
                domain = split[0]
                line = '/'.join(split[1:])

            split = line.split(sep)
            username = split[0]

            if len(split) < 2:
                password = None
            else:
                password = sep.join(split[1:])

            cred = Credential(username, password, 'Import', None, None, domain, 0)
            creds.add(cred)

        return creds

    def ljust(item: str, size: int) -> str:
        '''
        Wrapper around the default ljust function that truncates oversized strings
        with a placeholder.

        Parameters:
            item        Item to ljust
            size        Size as for ljust function

        Returns:
            str         Formatted string
        '''
        e_size = size - 5

        if len(item) > e_size:
            item = item[0:e_size] + '...'

        return item.ljust(size)

    def reset_count() -> None:
        '''
        Resets the credential counter to one.

        Parameters:
            None

        Returns:
            None
        '''
        Credential.count = itertools.count(1)

    def filter_imports() -> set[Credential]:
        '''
        Returns a set of credentials where all credentials with the note 'Import'
        are filtered.

        Parameters:
            None

        Returns:
            None
        '''
        creds = Credential.from_file()
        creds = set(filter(lambda x: x.note != 'Import', creds))
        return creds

    def get_by_id(c_id: int, credentials: set[Credential]) -> Credential:
        '''
        Find a credential by id.

        Parameters:
            c_id            Desired credential id

        Returns:
            credential      Corresponding credential object
        '''
        try:
            return next(filter(lambda x: x.id == c_id, credentials))

        except StopIteration:
            return None
