from setuptools import setup, find_packages

setup(
    name="apisentinel",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "geoip2>=4.0.0",
    ],
    author="API Sentinel",
    author_email="info@apisentinel.com",
    description="API Sentinel SDK for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/apisentinel/sdk-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)