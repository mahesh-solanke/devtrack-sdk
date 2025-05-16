from setuptools import find_packages, setup

setup(
    name="devtrack_sdk",
    version="0.1.0",
    description="Plug-and-play request tracking middleware for FastAPI apps.",
    author="Mahesh Solanke",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["fastapi", "httpx", "starlette"],
    python_requires=">=3.7",
)
