from setuptools import find_packages, setup

setup(
    name="devtrack-sdk",
    version="0.4.1",
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
    install_requires=["fastapi", "httpx", "starlette", "django>=4.0.0"],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: FastAPI",
    ],
    entry_points={
        "console_scripts": [
            "devtrack = devtrack_sdk.cli:app",
        ],
    },
)
