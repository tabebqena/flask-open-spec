import setuptools

version = "0.2.0-dev"

requirements = [
    "apispec>=4.7.1",
    "click>=8.0.1",
    "Flask",
    "blinker",
    "marshmallow",
    "PyYAML",
    "openapi-spec-validator",
    "deepdiff",
]


setuptools.setup(
    name="open_oas",
    version=version,
    author="Ahmad Yahia",
    python_requires=">=3.8.5",
    install_requires=requirements,
    packages=setuptools.find_packages(),  # ["open_oas"],
    # package_dir={"open_oas": "open_oas"},
)
