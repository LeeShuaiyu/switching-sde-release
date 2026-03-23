from setuptools import find_packages, setup


setup(
    name="switching-sde-release",
    version="0.1.0",
    description="Reproducible switching SDE release repository with legacy artifact compatibility",
    author="Switching SDE Team",
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "switching_sde": [
            "config/*.yaml",
            "config/experiments/*.yaml",
        ]
    },
    install_requires=[
        "numpy>=1.23",
        "matplotlib>=3.6",
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "switching-sde=switching_sde.cli.main:main",
        ]
    },
)
