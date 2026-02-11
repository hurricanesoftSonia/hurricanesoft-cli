from setuptools import setup

setup(
    name='hurricanesoft-cli',
    version='0.5.0',
    packages=['hurricanesoft_cli'],
    package_dir={'hurricanesoft_cli': '.'},
    entry_points={
        'console_scripts': [
            'hs=hurricanesoft_cli.main:main',
        ],
    },
    python_requires='>=3.8',
)
