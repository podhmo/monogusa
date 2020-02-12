from setuptools import setup, find_packages


install_requires = ["handofcats>=3.1.1", "magicalimport", "prestring"]
dev_requires = ["black", "flake8", "mypy"]
tests_requires = ["pytest", "pytest-asyncio"]
web_requires = ["dictknife", "pydantic", "fastapi", "uvicorn", "async-asgi-testclient"]

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
    install_requires=install_requires,
    extras_require={
        "testing": tests_requires,
        "dev": dev_requires,
        "web": web_requires,
        "slack": ["slackbot", "python-dotenv"],
        "discord": ["discord.py", "python-dotenv"],
    },
    tests_require=tests_requires,
    test_suite="monogusa.tests",
    #     entry_points="""
    #       [console_scripts]
    #       monogusa = monogusa.cli:main
    # """,
)
