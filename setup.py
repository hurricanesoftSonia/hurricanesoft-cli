from setuptools import setup, find_packages

setup(
    name='hurricanesoft-cli',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hs=hurricanesoft_cli.main:main',
        ],
    },
    python_requires='>=3.8',
)
