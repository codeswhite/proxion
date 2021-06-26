import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proxion",
    version="0.9.0",
    description="Multi-threaded proxy checker with uptime and latency statistics",
    url="https://github.com/codeswhite/proxion",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'interutils',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'proxion = proxion:main',
        ],
    },
    author="Max G",
    author_email="max3227@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages()
)
