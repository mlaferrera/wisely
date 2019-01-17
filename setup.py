from setuptools import setup

setup(
    name='wisely',
    version='0.5.0',
    description='Simple secrets store for Google Cloud',
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/mlaferrera/wisely',
    author='Marcus LaFerrera',
    author_email='marcus@randomhack.org',
    keywords='secrets management, google cloud, google kms',
    include_package_data=True,
    install_requires=open('requirements.txt').read().split(),
    python_requires='>=3.5',
    license='MIT',
    packages=['wisely'],
    entry_points={'console_scripts': ['wisely=wisely:main']},
)
