"""
Klar Search Engine (KSE) - Setup Configuration
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="klar-search-engine",
    version="3.0.0",
    author="Oscyra Solutions",
    author_email="contact@oscyra.solutions",
    description="Privacy-first Swedish search engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CKCHDX/klar",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "Flask>=2.3.0",
        "PyQt6>=6.6.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "nltk>=3.8.1",
        "numpy>=1.24.0",
        "scikit-learn>=1.2.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "kse-server=kse.server.kse_server:main",
            "kse-gui=gui.kse_gui_main:main",
            "kse-crawler=scripts.start_crawler:main",
        ],
    },
)
