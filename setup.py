from setuptools import setup, find_packages

# Read the requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = f.read().splitlines()

setup(
    name="TriloDocs",
    version="1.0.0",
    description="TriloDocs Table Processor app for processing .docx tables",
    author="Denys Lykholit",
    author_email="d.lykholit@gmail.com",
    packages=find_packages(),
    py_modules=['run'],
    include_package_data=True,
    install_requires=install_requires
)
