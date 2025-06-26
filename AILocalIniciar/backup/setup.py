from setuptools import setup, find_packages

setup(
    name="backup_system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15.0',
        'py7zr>=0.20.5',
        'google-api-python-client>=2.0.0',
        'google-auth>=2.0.0',
        'google-auth-oauthlib>=0.4.0',
        'google-auth-httplib2>=0.1.0'
    ],
    entry_points={
        'console_scripts': [
            'iniciar_backup=backup.iniciar_backup:main',
        ],
    },
    python_requires='>=3.6',
    author="AILocal",
    description="Sistema de backup com integração Google Drive",
    keywords="backup, google drive, pyqt5",
) 