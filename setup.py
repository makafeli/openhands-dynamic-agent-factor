from setuptools import setup, find_packages

setup(
    name="openhands-dynamic-agent-factory",
    version="0.1.0",
    description="Dynamic agent factory for OpenHands that generates micro-agents based on technology keywords",
    author="OpenHands",
    author_email="openhands@all-hands.dev",
    packages=find_packages(),
    install_requires=[
        "openhands>=0.1.0",
        "dataclasses;python_version<'3.7'",
    ],
    extras_require={
        'python': ['ast', 'pylint'],
        'react': ['esprima', 'eslint'],
        'node': ['acorn', 'eslint'],
        'sql': ['sqlparse', 'sqlalchemy'],
        'all': [
            'ast', 'pylint',
            'esprima', 'eslint',
            'acorn',
            'sqlparse', 'sqlalchemy'
        ]
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)