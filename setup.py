import setuptools

# url = "https://github.com/pypa/sampleproject",

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cterasdk",
    version="3.1.2",
    author="CTERA Networks",
    author_email="support@ctera.com",
    description="CTERA Python SDK",
    long_description=long_description,
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.5',
)
