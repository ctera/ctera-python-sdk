import setuptools

# url = "https://github.com/pypa/sampleproject",

with open("README.md", "r") as fh:
    
    long_description = fh.read()

setuptools.setup(
    
    name = "cterasdk",
    
    version = "3.1",
    
    author = "Saimon Michelson",
    
    author_email = "saimon@ctera.com",
    
    description = "CTERA Python SDK",
    
    long_description = long_description,
    
    long_description_content_type = "text/markdown",
    
    packages = setuptools.find_packages(),
    
    include_package_data = True,
    
    classifiers = [
        
        "Programming Language :: Python :: 3",
        
        "License :: GNU General Public License :: 3",
        
        "Operating System :: OS Independent",
        
    ],
    
    python_requires = '>=3.5',
    
)