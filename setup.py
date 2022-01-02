from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setup(
    name="stocks",
    version="0.1.0",
    description="Stocks",
    author="Adam Rose",
    author_email="emanuele.cannizzaro@gmail.com",
    url="https://github.com/emanuelecannizzaro/stocks",
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    exclude_package_data={'': ['.gitignore']},
    # Using this instead of MANIFEST.in - https://pypi.org/project/setuptools-git/
    setup_requires=['setuptools-git'],
    install_requires=[
    ],
)
