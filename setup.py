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
        'boto3==1.18.26',
        'jinja2==3.0.1',
        'musicbrainzngs==0.7.1',
        'openpyxl==3.0.7',
        'pandas==1.3.2',
        'pdfkit==0.6.1',
        'pdfplumber==0.5.28',
        "pypdf2==1.26.0",
        'pyyaml==5.4.1',
        'sqlalchemy==1.4.23',
        'tabula-py==2.2.0',
        'tqdm==4.62.1'
    ],
    entry_points={
        'console_scripts': ['musicie = musicie.cli:cli']
    }
)