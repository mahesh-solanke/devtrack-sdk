from setuptools import find_packages, setup

setup(
    name="devtrack-sdk",
    version="0.2.3",
    description="Middleware-based API analytics and observability tool for FastAPI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mahesh Solanke",
    author_email="maheshsolanke69@gmail.com",
    url="https://github.com/mahesh-solanke/devtrack-sdk",
    license="MIT",
    packages=find_packages(),
    install_requires=["fastapi", "httpx", "starlette"],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "devtrack = devtrack_sdk.cli:app",
        ],
    },
)
