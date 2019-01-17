## wisely - simple secrets store for Google Cloud KMS

# Overview

Wisely is a simple secrets management library. Secrets are stored in an encrypted
form in Google Cloud Storage (GCS) buckets. Encryption routines leverage Google
Cloud's Key Management Store (KMS) service. Once secrets are decrypted, they are
readily available as a `dict()` within Python.

# Installation

    pip3 install wisely

# Usage

## Configuration

Wisley requires a simple configuration before you get started. For the sake of,
simplcity, this documentation assumes that you have already [created a GCS bucket](https://cloud.google.com/storage/docs/creating-buckets)
for secret storage, and have also [created a KMS keyring and key](https://cloud.google.com/kms/docs/creating-keys).

Let's get familar with some basic terms required for the configuration:

- **project_id**: Google Cloud project ID
- **secret_path**: Filename of secret file in GCS
- **keyring_id**: KMS keyring name
- **crypto_id**: KMS key name within the specified keyring
- **location_id**: Google Cloud zone the keyring is located in
- **bucket_name**: GCS bucket name to store secrets
- **mode**: Method used to parse secrets. Valid options are kv, json, or raw
- **delim**: Delimiter for key/values when in mode kv

  wisley.cfg

  ***

  The wisely configuration file is a simple `yaml` file. By default, wisely will
  look for the configuration file in `~/.wisley`. The basic construct is:

       [secret_name]
       project_id = my_google_project-10234
       secret_path = secrets.txt
       keyring_id = my_soooper_keyring
       crypto_id = the_key
       location_id = us-west1-a
       bucket_name = sooper-secret-bucket-12312321
       mode = kv
       delim = :

  If the `[global]` configuration section exists, wisley will load those first. For
  instance, if there is a shared `project_id` across all of your secrets, you may
  want to define `project_id` in `[global]`:

           [global]
           project_id = my_google_project-10234

           [secret_name_one]
           secret_path = secrets-one.txt
           keyring_id = my_soooper_keyring
           crypto_id = the_key_one
           location_id = us-west1-a
           bucket_name = sooper-secret-bucket-12312321

           [secret_name_two]
           secret_path = secrets-two.txt
           keyring_id = my_soooper_keyring
           crypto_id = the_key_two
           location_id = us-west1-a
           bucket_name = sooper-secret-bucket-12312321

  Environment Variables

  ***

  If no configuration options are defined, wisely will attempt to gather the
  required configuration options from environment variables:

       WISELY_PROJECT_ID=my_google_project-10234
       WISELY_SECRET_PATH=secrets.txt
       WISELY_KEYRING_ID=my_soooper_keyring
       WISELY_CRYPTO_ID=the_key
       WISELY_LOCATION_ID=us-east1-a
       WISELY_BUCKET_NAME=sooper-secret-bucket-12312321

## Adding/Updating Secret Configuration

Wisley provides a simple cli interface that allows for adding secret configurations:

    wisley secret_name --path secrets.txt --project my_google_project-10234 \
            --keyring my_soooper_keyring --crypto the_key \
            --bucket sooper-secret-bucket-12312321 --location us-west1-a

Likewise, if you would like to update an individual secret configuration, such as
updating the bucket name, simply add the `--update` argument:

    wisley secret_name --update --bucket new-secret-bucket-121321

## Adding Secrets

A secrets file can be plaintext, key/value pairs, or json. By default, wisely will
assume that the mode is a key/value pair.

For example:

        USER=joebob
        PASS=soopersecret321

Or, if json:

        {"USER": "joebob", "PASS": "soopersecret321"}

The secrets file may also be plaintext, which will not be parsed in any way by wisely.

To add a new secret, simply run:

        wisely encrypt secret_name cleartext-file.txt

Once completed, the encrypted file will be encrypted and uploaded to the specified
GCS bucket. If you want to update the encrypted secrets file:

        wisely decrypt secret_name -o cleartext-file.txt

## Using in scripts

Using wisely in scripts is extremely easy. There are two ways to instantiate `Wisley`.

You can either pass all of the required configuration options:

        from wisely import Wisely

        project_id = 'my_google_project-10234'
        secret_path = 'secrets.txt'
        keyring_id = 'my_soooper_keyring'
        crypto_id = 'the_key'
        location = 'us-west1-a'
        bucket_name = 'sooper-secret-bucket-12312321'
        mode = 'json'

        wise = Wisley(
            project_id=project_id, secret_path=secret_path, keyring_id=keyring_id,
            crypto_id=crypto_id, location=location, bucket_name=bucket_name,
            mode=mode)

        secrets = wise.decrypt()

        user = secrets['USER']
        pass = secrets['PASS']

        print('User: {}, Pass: {}'.format(user, pass))

Or, if all enviroment variables are properly defined:

        from wisely import Wisely

        wise = Wisely()
        secrets = wise.decrypt()

        user = secrets['USER']
        pass = secrets['PASS']

        print('User: {}, Pass: {}'.format(user, pass))
