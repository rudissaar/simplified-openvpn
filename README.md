# Simplified OpenVPN

Simple management interface for OpenVPN Community Edition that makes generating new clients fast and easy, it also provides extra functionalities like sharing client configuration files via web interface.

### Requirements
* python3.x
* python3-pystache
* python3-slugify
* python3-openssl
* python3-flask

### Server Structure
In order to make Simplified OpenVPN work, the OpenVPN server needs to have
following names for certificates/keys:

```
{SERVER_DIR}/ca.crt   - Authority Certificate
{SERVER_DIR}/ta.key   - TLS Auth Key
```

For Easy RSA your configuration should have following structure:

```
{EAST_RSA_DIR}/vars          - File that holds pre-filled values to generate new keys
{EAST_RSA_DIR}/openssl.cnf   - File that contains settings for you OpenSSL version
```
