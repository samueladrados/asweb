from setuptools import setup, find_packages

setup(
    name="asweb_core",
    version="1.0.0",
    author="Samuel Adrados",
    description="Core research algorithms for ASWEB",
    # Automatically discovers the 'src' package containing the logic
    packages=find_packages(), 
    # Required runtime dependencies
    install_requires=[
        "Flask==2.3.2",
        "gensim==4.3.1",
        "nltk==3.8.1",
        "numpy==1.23.5",
        "scikit-learn==1.2.2",
        "scipy==1.10.1",
        "sympy==1.12",
        "tensorflow==2.12.0",
        "torch==2.0.1",
    ],
)