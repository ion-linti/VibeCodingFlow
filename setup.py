# setup.py
from setuptools import setup, find_packages

setup(
    name="VibeCodingFlow",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "vibe=VibeCodingFlow.cli:app",
        ],
    },
)