"""

Wisely - Simple Secrets Store

"""

import os
import json
import logging
import configparser

from argparse import RawDescriptionHelpFormatter, ArgumentParser
from pathlib import Path

from wisely.googlekms import Cipher

log = logging.getLogger(__name__)

CONFIG = "{}/.wisely".format(str(Path.home()))

class Wisely:

    def __init__(self, secret=None, configfile=None, settings={}, outfile=None, source=None, mode='kv', delim='='):
        """
        Wisely

        :param str secret: (optional) Secret name defined in configuration file
        :param str configfile: (optional) Wisely configuration file to load
        :param dict settings: (optional) Settings defining required attributes
        :param str outfile: (optional) Local file to save encrypted/decrypted content to
        :param str source: (optional) Local source file to encrypted/decrypt
        :param str mode: (Default: kv) Format to return data. (json, kv, raw)
        :param str delim: Delimiter when splitting secrets in key/value mode

        """
        self.secret = secret
        self.settings = settings
        self.outfile = outfile
        self.configfile = configfile
        self.source = source
        self.settings['mode'] = mode
        self.settings['delim'] = delim

        self.load_config()

    def load_config(self):
        """
        Load wisely configuration file

        """
        if self.configfile:
            self.parsed_config = configparser.ConfigParser()
            self.parsed_config.read(self.configfile)

            if 'global' in self.parsed_config:
                for opt in self.parsed_config.options('global'):
                    self.settings[opt] = self.parsed_config.get('global', opt)

            try:
                for opt in self.parsed_config.options(self.secret):
                    self.settings[opt] = self.parsed_config.get(self.secret, opt)
            except configparser.NoSectionError:
                pass

        else:
            self.settings['secret_path'] = os.getenv('WISELY_SECRET_PATH')
            self.settings['crypto_id'] = os.getenv('WISELY_CRYPTO_ID')
            self.settings['project_id'] = os.getenv('WISELY_PROJECT_ID')
            self.settings['bucket_name'] = os.getenv('WISELY_BUCKET_NAME')
            self.settings['keyring_id'] = os.getenv('WISELY_KEYRING_ID')
            self.settings['location_id'] = os.getenv('WISELY_LOCATION_ID')

    def save_config(self):
        """
        Save wisely configuration file

        """
        try:
            with open(self.configfile, 'w') as configfile:
                self.parsed_config.write(configfile)
        except FileNotFoundError:
            log.error("{} does not exist.".format(self.configfile))

    def section_update(self, update=False, **kwargs):
        """
        Add/Update wisely configuration

        :param bool update: (optional) Define whether configuration file should be updated
        :param kwargs: Configuration options to be added to section

        """
        if self.parsed_config.has_section(self.secret) and not update:
            log.error("Section already exists..unable to add {} (use --update)".format(self.secret))
            return

        if not update:
            self.parsed_config.add_section(self.secret)

        for option, value in kwargs.items():
            if value:
                self.parsed_config.set(self.secret, option, value)

        self.save_config()

    def save(self, content):
        """
        Save content to a local file

        :param content: Content to be locally saved

        """
        with open(self.outfile, 'x') as outfile:
            outfile.write(content)

    def decrypt(self):
        """
        Decryption handler

        """
        ciphertext = None

        self.cipher = Cipher(**self.settings)

        if self.source:
            with open(self.source, 'rb') as content:
                ciphertext = content.read()

        cleartext = self.cipher.decrypt(ciphertext)
        secrets = None

        if self.outfile:
            self.save(cleartext)

        if self.settings['mode'] == 'json':
            secrets = json.loads(cleartext)
        elif self.settings['mode'] == 'kv':
            secrets = {}
            for line in cleartext.splitlines():
                key, value = line.split(self.settings['delim'], 1)
                secrets[key.strip()] = value.strip()
        elif self.settings['mode'] == 'raw':
            secrets = cleartext

        return secrets

    def encrypt(self):
        """
        Encryption handler

        """

        with open(self.source, 'rb') as content:
            plaintext = content.read()

        self.cipher = Cipher(**self.settings)
        ciphertext = self.cipher.encrypt(plaintext)

        if self.outfile:
            self.save(ciphertext)
        else:
            self.cipher.upload_file(ciphertext)

def main():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    decrypt = subparsers.add_parser('decrypt')
    decrypt.add_argument('secret', help='Secret name to decrypt')
    decrypt.add_argument('-s', '--source', dest='source', default=None, help='Source file to decrypt')
    decrypt.add_argument('-o', '--outfile', dest='outfile', default=None, help='File to save results to')
    decrypt.add_argument('-c', '--config', dest='config', default=CONFIG, help='wisley configuration file')

    encrypt = subparsers.add_parser('encrypt')
    encrypt.add_argument('secret', help='Secret name to encrypt')
    encrypt.add_argument('source', help='File to encrypt')
    encrypt.add_argument('-o', '--outfile', dest='outfile', default=None, help='File to save results to')
    encrypt.add_argument('-c', '--config', dest='config', default=CONFIG, help='wisley configuration file')

    config = subparsers.add_parser('config')
    config.add_argument('secret', help='Unique Secret Name')
    config.add_argument('-c', '--config', dest='config', default=CONFIG, help='wisley configuration file')
    config.add_argument('--update', dest='update', action='store_true', help='Update configuration')
    config.add_argument('--path', dest='path', help='Path encrypted content should be saved to in GCS')
    config.add_argument('--crypto', dest='crypto', default=None, help='Crypto Key')
    config.add_argument('--project', dest='project', default=None, help='Google Cloud project ID')
    config.add_argument('--bucket', dest='bucket', default=None, help='GCS Bucket')
    config.add_argument('--keyring', dest='keyring', default=None, help='KMS Keyring')
    config.add_argument('--location', dest='location', default=None, help='Google Cloud Zone for KMS')

    view = subparsers.add_parser('view')
    view.add_argument('-c', '--config', dest='config', default=CONFIG, help='wisley configuration file')

    args = parser.parse_args()

    if args.command == 'decrypt':
        wise = Wisely(secret=args.secret, configfile=args.config, outfile=args.outfile, source=args.source)
        content = wise.decrypt()
        if content:
            print('Successfuly decrypted {}'.format(args.secret))
        if not args.outfile:
            print(content)
    elif args.command == 'encrypt':
        wise = Wisely(secret=args.secret, configfile=args.config, outfile=args.outfile, source=args.source)
        wise.encrypt()
        print('Successfuly encrypted {}'.format(args.secret))
    elif args.command == 'config':
        print('Saving configuration for {}'.format(args.secret))
        wise = Wisely(secret=args.secret, configfile=args.config)
        wise.section_update(
            update=args.update, path=args.path, crypto_id=args.crypto,
            project_id=args.project, bucket_name=args.bucket,
            keyring_id=args.keyring, location_id=args.location
            )
    elif args.command == 'view':
        try:
            with open(args.config, 'r') as config:
                print(config.read())
        except FileNotFoundError:
            print('{} does not exists, unable to read configuration file'.format(args.config))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()