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
        'jinja2==3.0.1',
        'musicbrainzngs==0.7.1',
        'openpyxl',
        'pandas==1.3.2',
        'pdfkit==0.6.1',
        'pdfplumber==0.5.28',
        "pypdf2==1.26.0",
        'pyyaml==5.4.1',
        'tabula-py==2.2.0'
    ],
    entry_points={
        'console_scripts': ['musicie = musicie.cli:cli']
    }
)