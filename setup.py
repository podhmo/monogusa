from setuptools import setup, find_packages


setup(
    classifiers=[
        # "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.7",
    packages=find_packages(exclude=["monogusa.tests"]),
    install_requires=["handofcats>=3.2.0", "magicalimport>=0.9.1", "prestring>=0.8.2"],
    extras_require={
        "testing": ["pytest", "pytest-asyncio"],
        "dev": ["black", "flake8", "mypy"],
        "web": ["dictknife", "pydantic", "fastapi", "uvicorn", "async-asgi-testclient"],
        "slack": ["slackbot", "python-dotenv"],
        "discord": ["discord.py", "python-dotenv"],
    },
    tests_require=["pytest", "pytest-asyncio"],
    test_suite="monogusa.tests",
    #     entry_points="""
    #       [console_scripts]
    #       monogusa = monogusa.cli:main
    # """,
)
