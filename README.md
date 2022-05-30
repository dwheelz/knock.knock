# knock.knock
fwknopin' on Heaven's door

## Main principles/Goals:

This allows for a relatively simple and secure way to do the following:
 - Store fwknop Stanzas on a host
 - Knock for access to a port/service (via the fwknop client)

For more information on the Single Packet Authorization/Fwknop implementation, please review: https://www.cipherdyne.org/fwknop/docs/fwknop-tutorial.html#quick-start

Before use, the client certificates (client_priv and client_pub) should be updated with some new Elipict Curve certs. Please refer to supported types for the installed
version of OpenSSL (via the Cryptography package).
The same also applies to the bundled 'server_pub' certificate.

## Generating the 'secret_string' (Needs improving)

To generate the encrypted byte-string (In Python terms, I'm sure many people have opinions about my terminology here..) used for generating the encrypted stanzas,
one of the following will need to occur:

- Create a venv and install the pip packages in run_scripts/py/requirements.txt
- Spawn an interactive docker container based off the bundled Dockerfile

Once you are in your environment, open an interactive Python session and interact with `EncryptedConfigData`.
Example code snippet below:

```
encryptor = EncryptedConfigData()
# All keys must exist in the 'Keys' DIR in run-scripts/py/common
encryptor.encrypt_to_file("file_name_of_your_private_key.pem", "super secret stuff")
```

The 'Super secret stuff' (i.e the stanza you are encrypting) will need to be a string and conform to this pattern:

```
--user = USERNAME --your_ip = IP_OF_HOST_OR_OMITTED --port = tcp/80 --host = IP_OF_SPA_SERVER --key = YOUR_KEY_BASE_64 --hmac = YOUR_HMAC_BASE_64[END]
```
Please note: the `--your_ip` is optional, if it is omitted your external IP will be resolved for you

The output of `encryptor.encrypt_to_file` will be put into `/data/secret_string.txt`

## The Docker-compose files
- config-docker-compose: This will generate the encrypted stanzas, and place them in `config`
- knock-docker-compose: Once the stanzas are generated, this will perform the knock

## Improvements
- The Stanza generation shouldn't be a two stage process, this is a hangover from a design change (and wish to allow unencrypted stanzas (not possible via dockers))
- Is docker-compose the right choice? 
- Test cases....

## Info to add
It is possible to generate unencrypted stanzas if this suites the use case. There is a bash script in `docker-runtime-unsecure` that will run each stanza in the
`config` DIR.
