from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openhands-dynamic-agent-factor",
    version="1.0.2",
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful system for analyzing and generating technology-specific agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/openhands-dynamic-agent-factor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "typing-extensions>=4.0.0",
        "pydantic>=2.0.0",
        "PyYAML>=6.0",
        "mkdocs>=1.4.0",
        "mkdocs-material>=9.0.0",
        "types-requests>=2.25.0",
        "types-beautifulsoup4>=4.9.0",
        "types-PyYAML>=6.0",
        "dataclasses-json>=0.5.7",
        "webbrowser>=0.10.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "pylint>=2.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openhands=openhands_dynamic_agent_factory.core.cli:main",
        ],
    },
)
