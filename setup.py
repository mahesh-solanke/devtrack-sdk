from setuptools import find_packages, setup

setup(
    name="devtrack-sdk",
    version="0.4.2",
    description=(
        "Middleware-based API analytics and observability tool for FastAPI and Django"
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mahesh Solanke",
    author_email="maheshsolanke69@gmail.com",
    url="https://github.com/mahesh-solanke/devtrack-sdk",
    license="MIT",
    packages=find_packages(),
    package_data={
        "devtrack_sdk": [
            "dashboard/dist/**/*",
            "dashboard/index.html",
        ],
    },
    include_package_data=True,
    install_requires=[
        "duckdb>=1.1.0",
        "requests>=2.31",
        "rich>=13.3",
        "typer>=0.9",
    ],
    extras_require={
        "fastapi": ["fastapi>=0.90"],
        "django": ["django>=4.0.0"],
        "all": ["fastapi>=0.90", "django>=4.0.0"],
        "dev": [
            "django>=4.0.0",
            "fastapi>=0.90",
            "httpx>=0.24",
            "pytest>=8.0",
            "pytest-mock>=3.12",
            "tomli>=2.0; python_version < '3.11'",
            "uvicorn>=0.34",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.2",
        "Framework :: FastAPI",
    ],
    entry_points={
        "console_scripts": [
            "devtrack = devtrack_sdk.cli:app",
        ],
    },
)
