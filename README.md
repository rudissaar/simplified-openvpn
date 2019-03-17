# Simplified OpenVPN

Simple client creation management interface for OpenVPN Community Edition that makes generating new clients fast and easy, it also provides extra functionalities like sharing client configuration files via web interface.

[![asciicast](https://asciinema.org/a/234347.svg)](https://asciinema.org/a/234347)

### Requirements
* python3.x
* python3-pystache
* python3-slugify
* python3-flask

### Server Structure
In order to make Simplified OpenVPN work, the OpenVPN server needs to have
following names and structure:

```
{SERVER_DIR}/ta.key   - TLS Auth Key
```

If you are using Easy RSA 2 your configuration should have following structure:

```
{EAST_RSA_DIR}/vars          - File that holds pre-filled values to generate new keys
{EAST_RSA_DIR}/openssl.cnf   - File that contains settings for you OpenSSL version
```

For Easy RSA 3 you don't need any special modification, just make sure that binary exists.

```
{EAST_RSA_DIR}/easyrsa   - Easy RSA 3 binary
```

### Client Creation

To create new clients and their configuration files with Simplified OpenVPN just use:

```
./sovpn.py
```

Or if you prefer longer version:

```
./sovpn.py create
```

There is also option to pre-fill name for client that you are going to create,
but you can only create 1 client at the time.

```
./sovpn.py create <pretty-name>
```

### Client Revocation

In order to use client revocation functionality, your OpenVPN server setup needs to include CRL.

```
./sovpn.py revoke <common-name>
```

### File Sharing

Simplified OpenVPN comes with built-in sharing functionality, in order to share generated configuration files with specific clients use following command:

```
./sovpn.py share <common-name> ...
```

To open sharing for all existing clients use share command without any argument, but every client needs to know their own sharing hash.

```
./sovpn.py share
```

Keep in mind that sharing functionality is optional.

### Miscellaneous

If you are struggling with installation of OpenVPN server itself, then the following shell scripts might help you out:

* Debian
[debian-post-install/openvpn.sh](https://github.com/rudissaar/linux-config-scripts/blob/master/debian-post-install/openvpn.sh)
* Fedora
[fedora-post-install/openvpn.sh](https://github.com/rudissaar/linux-config-scripts/blob/master/fedora-post-install/openvpn.sh)
