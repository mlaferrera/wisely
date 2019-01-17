"""
Overview
========

Download an encrypted file from Google Cloud storage and decrypt
it using Google KMS

"""

import base64
import logging
import os
import io
import magic

import googleapiclient.discovery
from google.cloud import storage

log = logging.getLogger(__name__)


class Cipher:
    def __init__(self, **settings):
        """
        Decrypts content of file using KMS from GCS and saves it locally.

        :param str cipherfile: (optional) File on GCS to decrypt/encrypt
        :param str keyring_id: Name of KMS Keyring
        :param str crypto_id: Name of Keyring Key
        :param str project_id: Google Cloud project ID
        :param str bucket_name: (optional) Google Cloud Storage bucket name
        :param str secret_path: Path to encrypted file in GCS

        """

        self.cipherfile = settings.get('secret_path')
        self.crypto_id = settings.get('crypto_id')
        self.project_id = settings.get('project_id')
        self.bucket_name = settings.get('bucket_name')
        self.keyring_id = settings.get('keyring_id')
        self.location_id = settings.get('location_id')

        # Creates an API client for the KMS API.
        self.kms_client = googleapiclient.discovery.build(
            'cloudkms', 'v1', cache_discovery=False
        )

        # The resource name of the CryptoKey.
        self.key_name = 'projects/{}/locations/{}/keyRings/{}/cryptoKeys/{}'.format(
            self.project_id, self.location_id, self.keyring_id, self.crypto_id
        )

        if self.bucket_name:
            self.gcs_client = self._get_storage_client()
            self.bucket = self.gcs_client.bucket(self.bucket_name)

    def decrypt(self, ciphertext=None):
        """
        Decrypt encrypted file in GCS

        """

        if not ciphertext:
            # Read encrypted data from the input file.
            ciphertext = self.download_file()

        # Use the KMS API to decrypt the data.
        crypto_keys = self.kms_client.projects().locations().keyRings().cryptoKeys()
        request = crypto_keys.decrypt(
            name=self.key_name,
            body={'ciphertext': base64.b64encode(ciphertext).decode('ascii')},
        )
        response = request.execute()

        return base64.b64decode(response['plaintext'].encode('ascii')).decode()

    def encrypt(self, plaintext):
        """
        Encrypts data from plaintext to ciphertext using KMS and push
        ciphertext to GCS

        """

        # Use the KMS API to encrypt the data.
        crypto_keys = self.kms_client.projects().locations().keyRings().cryptoKeys()
        request = crypto_keys.encrypt(
            name=self.key_name,
            body={'plaintext': base64.b64encode(plaintext).decode('ascii')},
        )
        response = request.execute()

        return base64.b64decode(response['ciphertext'].encode('ascii'))

    def upload_file(self, ciphertext):
        """
        Upload a file to a given Cloud Storage bucket

        :param str ciphertext: Content to be uploaded to GCS

        :returns: True

        """

        blob = self.bucket.blob(self.cipherfile)
        content_type = magic.from_buffer(ciphertext, mime=True)
        blob.upload_from_string(ciphertext, content_type=content_type)
        return True

    def download_file(self):
        """
        Download a file from GCS

        """
        blob = self.bucket.blob(self.cipherfile)
        return blob.download_as_string()

    def _get_storage_client(self):
        return storage.Client(project=self.project_id)
