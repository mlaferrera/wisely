from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='wisely',
    version='0.5.2',
    description='Simple secrets store for Google Cloud',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/mlaferrera/wisely',
    author='Marcus LaFerrera',
    author_email='marcus@randomhack.org',
    keywords='secrets management, google cloud, google kms',
    include_package_data=True,
    install_requires=[
        "python-magic~=0.4.15",
        "google-api-python-client~=1.7.7",
        "google-cloud-storage>=1.13.2,<1.17.0",
        "google-auth-httplib2~=0.0.3",
        "google-auth>=1.6.2,<1.14.0",
    ],
    python_requires='>=3.5',
    license='MIT',
    packages=['wisely'],
    entry_points={'console_scripts': ['wisely=wisely:main']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Security',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
