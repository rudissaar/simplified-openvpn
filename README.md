# Simplified OpenVPN

Simple client creation management interface for OpenVPN Community Edition that makes generating new clients fast and easy, it also provides extra functionalities like sharing client configuration files via web interface.

## `Important Notice`
> This project is currently only tested on Debian 9 GNU/Linux and only works with Easy RSA 2, soon it should be also be compatible with Easy RSA 3.

### Requirements
* python3.x
* python3-pystache
* python3-slugify
* python3-openssl
* python3-flask

### Server Structure
In order to make Simplified OpenVPN work, the OpenVPN server needs to have
following names and structure for certificates/keys:

```
{SERVER_DIR}/ca.crt   - Authority Certificate
{SERVER_DIR}/ta.key   - TLS Auth Key
```

For Easy RSA your configuration should have following structure:

```
{EAST_RSA_DIR}/vars          - File that holds pre-filled values to generate new keys
{EAST_RSA_DIR}/openssl.cnf   - File that contains settings for you OpenSSL version
```
