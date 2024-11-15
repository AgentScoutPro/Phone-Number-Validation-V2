
from setuptools import setup, find_packages

setup(
    name="phone-validator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'streamlit==1.29.0',
        'pandas==2.1.4',
        'phonenumbers==8.13.25',
        'openpyxl==3.1.2',
        'requests==2.31.0'
    ],
)
