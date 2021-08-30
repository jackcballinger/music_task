from setuptools import setup

setup(
    name='musicie',
    description='Amplify Homework - Data Engineering by Jack Ballinger',
    author='Jack Ballinger',
    author_email='jackcballinger@gmail.com',
    python_requires='>=3',
    py_modules=['musicie'],
    setup_requires=['setuptools_scm'],
    install_requires=[
        'musicbrainzngs==0.7.1',
        'openpyxl',
        'pandas==1.3.2',
        'pdfplumber==0.5.28',
        'pyyaml==5.4.1',
        'tabula-py==2.2.0'
    ],
    entry_points={
        'console_scripts': ['musicie = musicie.cli:cli']
    }
)