import setuptools

version = "0.1.0-dev"

requirements = [
    "apispec>=4.7.1",
    "click>=8.0.1",
    "Flask",
    "marshmallow",
    "PyYAML",
    "openapi-spec-validator",
]


setuptools.setup(
    name="open_spec",
    version=version,
    author="Ahmad Yahia",
    python_requires=">=3.8.5",
    install_requires=requirements,
    packages=["open_spec"],
    package_dir={"open_spec": "open_spec"},
)
