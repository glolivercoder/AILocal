from setuptools import setup, find_packages

setup(
    name="backup_system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "py7zr>=0.20.5",
        "humanize>=4.7.0"
    ],
    python_requires=">=3.9",
    author="AILocal",
    description="Sistema de backup com interface gráfica e compressão 7z",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 