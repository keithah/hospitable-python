"""
Setup configuration for hospitable-python
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="hospitable-python",
    version="0.1.0",
    author="Keith",
    author_email="keith@example.com",
    description="Python SDK for Hospitable Public API v2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/hospitable-python",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/hospitable-python/issues",
        "Documentation": "https://github.com/your-username/hospitable-python/blob/main/docs/README.md",
        "Source Code": "https://github.com/your-username/hospitable-python",
        "API Documentation": "https://developer.hospitable.com/docs/public-api-docs/",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
            "pre-commit>=2.20",
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.18",
        ],
    },
    keywords=[
        "hospitable",
        "vacation rental",
        "short-term rental",
        "airbnb",
        "vrbo",
        "booking",
        "property management",
        "api",
        "sdk",
        "client",
    ],
    include_package_data=True,
    zip_safe=False,
)