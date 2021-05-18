### ctfcred

----

During *CTFs* it is common to obtain several different usernames and passwords.
Just storing these inside of text files becomes confusing very quickly and accessing
them in this way is not really fast. *ctfcred* is designed to allow fast, organized and
simple access to *CTF* credentials. Credentials are stored as plaintext in a ``.yml``
file and are accesses via *rofi*.

**Do not use this tool to store real sensitive data!**


### Table of Contents

----

- [Installation](#installation)
- [Usage](#usage)
- [Updating and Cloning Credentials](#updating-and-cloning-credentials)
- [Import and Export](#import-and-export)
- [Default Values](#default-values)
- [Warning](#warning)


### Installation

----

*ctfcred* can be build and installed as a *pip package*. The following command installs *ctfcred*
for your current user profile:

```console
$ git clone https://github.com/qtc-de/ctfcred
$ cd ctfcred
$ python3 setup.py sdist
$ pip3 install dist/*
```

*ctfcred* also supports autocompletion for *bash*. To take advantage of autocompletion, you need to have the
[completion-helpers](https://github.com/qtc-de/completion-helpers) project installed. If setup correctly, just
copying the [completion script](./resources/bash_completion.d/ctfcred) to your ``~/.bash_completion.d`` folder enables
autocompletion.

```console
$ cp resources/bash_completion.d/ctfcred ~/bash_completion.d/
```

Furthermore, there are some external dependencies:

* **rofi** (required): a working installation of *rofi* is required, as *rofi* is used to display and access the stored
  credentials.

* **libnotify** and a **notification server** (optional): These are shipped per default on most
  distributions. Just type ``$ notify-send test`` to check if they are available.
  If not, read about [desktop notifications](https://wiki.archlinux.org/index.php/Desktop_notifications)
  and decide if you want to install them. *ctfcred* uses the notification server to display messages,
  which values were copied to the clipboard. It is nice to have, but not required.


### Usage

----

The first thing you probably want to do with *ctfcred* is to add some credentials. Credentials can be added
by using the following argument format:

```console
[qtc@kali ~]$ ctfcred <USERNAME> <PASSWORD> <NOTE>
```

Each of this values is optional. You do not have to specify a *password* or a *note* and you can use empty strings
for *username* or *password* to get to the next argument. Let's add some credentials:

```console
[qtc@kali ~]$ ctfcred timmy password123 'Found on SMB share 10.10.10.3'
[qtc@kali ~]$ ctfcred carol carolsSecurePassword 'Carols AD Credentials' --domain example.com --url '\\10.10.10.2'
[qtc@kali ~]$ ctfcred peter pet3rRul35 'Peters GitLab password' --url 'https://gitlab.example.com' --otp e1euj1ßdhsdhdasd1
[qtc@kali ~]$ ctfcred peterTheInsaneFighter securePassword 'Peters Gaming password' --url 'https://games.example.com' --alias peter_gaming
```

After running the above commands, a plain run of *ctfcred* (without any arguments) starts *rofi* and displays the following
view:

![Rofi View](https://tneitzel.eu/73201a92878c0aba7c3419b7403ab604/ctfcred.png)

Within *rofi*, *ctfcred* defines several keybindings for performing actions with the stored credentials.

* ``Ctrl+C``:    Copy Username
* ``Ctrl+c``:    Copy Password
* ``Ctrl+o``:    Copy OTP Value
* ``Ctrl+l``:    Copy URL Value
* ``Ctrl+D``:    Copy Domain
* ``Ctrl+F``:    Copy User with Domain
* ``Ctrl+X``:    Delete Credential
* ``Ctrl+K``:    Move Credential one Up
* ``Ctrl+J``:    Move Credential one Down


### Updating and Cloning Credentials

----

Credentials can be updated or cloned by using the ``--update`` or ``--clone`` command line switches. Both of these
operations expect you to enter some credential data as in the case of creating a new credential. However, instead of using
the data to add a new credential, *ctfcred* will display all available credentials in *rofi* and wait for you to select one.

In the case of ``--update``, the corresponding credential is updated with the data you have entered. In the case of ``--clone``
the credential is cloned and updated with the new data afterwards. Cloning a credential without updating one of it's properties
is not possible, as only unique credentials are allowed by *ctfcred*.

The update and clone operations only change data that is user specified and not empty. E.g. if you want to update the password
of a credential without changing it's username, you would run the following command:

```console
[qtc@kali ~]$ ctfcred '' newpassword --update
```


### Import and Export

----

*ctfcred* stores credentials in a plain text ``.yml`` file within your home directory (``~/.ctfcred.yml``). Copying this file to
a different machine is sufficient to export all of your stored credentials.

Apart from the *ctfcred* internal format of storing credentials, it is also possible to export or import credentials from other formats.
During *CTFs* it is quite common to obtain credential lists with in ``<USERNAME>:<PASSWORD>`` format. Such a list can be imported with
one of the following commands:

```console
[qtc@kali ~]$ cat cred_file.txt
alex:S3cur3P@55w0rd
timmy:insecurePassword:(
[qtc@kali ~]$ ctfcred --import-user-pass cred_file.txt

[qtc@kali ~]$ cat cred_file2.txt
example.com/alex:S3cur3P@55w0rd
example.org/timmy:insecurePassword:(
[qtc@kali ~]$ ctfcred --import-user-pass-domain cred_file2.txt

[qtc@kali ~]$ cat cred_file3.txt
example.com/alex,S3cur3P@55w0rd
timmy,insecurePassword:(
[qtc@kali ~]$ ctfcred --import-user-pass-domain cred_file3.txt --sep ,
```

In the second and third example, the ``--import-user-pass-domain`` option is required, as otherwise the domain prefix
would be interpreted as username. Apart from imports with usernames and passwords, *ctfcred* also allows to import
just usernames or passwords:

```console
[qtc@kali ~]$ cat users.txt
timmy
harry
[qtc@kali ~]$ ctfcred --import-user users.txt

[qtc@kali ~]$ cat passwords.txt
SecurePW!
MySecretPW.
[qtc@kali ~]$ ctfcred --import-pass passwords.txt
```

Exports can be created in a similar way as imports and the same formats are supported. To create a list of username and passwords
separated by ``:`` you could run the following command:

```console
[qtc@kali ~]$ ctfcred --users-pass
carol:carolsSecurePassword
peter:pet3rRul35
peterTheInsaneFighter:securePassword
timmy:password123
```

It is also possible to print all permutations of the stored credentials by using the ``--mix`` switch:

```console
[qtc@kali ~]$ ctfcred --users-pass --mix
carol:carolsSecurePassword
carol:password123
carol:pet3rRul35
carol:securePassword
peter:carolsSecurePassword
peter:password123
peter:pet3rRul35
peter:securePassword
peterTheInsaneFighter:carolsSecurePassword
peterTheInsaneFighter:password123
peterTheInsaneFighter:pet3rRul35
peterTheInsaneFighter:securePassword
timmy:carolsSecurePassword
timmy:password123
timmy:pet3rRul35
timmy:securePassword
```

For creating simple wordlist of all available usernames or passwords, the ``--users`` and ``--passwords`` switches are sufficient:

```console
[qtc@kali ~]$ ctfcred --users
carol
peter
peterTheInsaneFighter
timmy
[qtc@kali ~]$ ctfcred --passwords
carolsSecurePassword
password123
pet3rRul35
securePassword
```


### Default Values

----

Default values are currently supported for the ``url`` and ``domain`` attribute of credentials. Both are set to ``None`` by default,
but they can be set to individual values on the command line:

```console
[qtc@kali ~]$ ctfcred --default-url https://example.com
[qtc@kali ~]$ ctfcred --default-domain example.com
```

When setting them manually, each copy or export operation that involves one of the corresponding attributes will use the default value,
when the credential does not has it set explicitly. The following output shows an example of this situation:

```console
[qtc@kali ~]$ ctfcred --users-domain
example.com/timmy
test.org/james
```


### Warning

----

This tool should not be used to store any sensitive information like your private usernames or passwords.
As mentioned above, all entered credentials are saved as plaintext on your disk. This behavior is insecure
and should only be used to store non sensitive data, like credentials obtained during a *CTF*.

Copyright 2021, Tobias Neitzel and the *ctfcred* contributors.
