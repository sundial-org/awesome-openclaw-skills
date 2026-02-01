from setuptools import setup

setup(
    name="skillsign",
    version="1.0.0",
    description="Sign and verify agent skill folders with ed25519 keys",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="FelmonBot (Parker)",
    url="https://github.com/felmonfekadu/skillsign",
    py_modules=["skillsign"],
    python_requires=">=3.8",
    install_requires=["cryptography>=41.0.0"],
    entry_points={
        "console_scripts": [
            "skillsign=skillsign:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Security :: Cryptography",
    ],
)
