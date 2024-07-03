from setuptools import setup, find_packages

setup(
    name="tradeOrderLibray",
    version="0.1",
    packages=find_packages(),
    install_requires=["ccxt"],
)