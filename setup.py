import os
import setuptools


VERSION = "0.0.1"


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


extra_files = package_files("vega_sim/vegahome")


setuptools.setup(
    name="vega-market-sim",
    version=VERSION,
    author="Vega",
    author_email="hi@vega.xyz",
    description="Simulator for running self-contained Vega chain on local PC",
    url="https://github.com/vegaprotocol/vega-market-sim",
    packages=setuptools.find_packages(exclude=["tests", "examples"]),
    package_data={"": extra_files, "vega_sim": ["bin/*"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["requests", "vega-api-client", "toml"],
    setup_requires=["wheel"],
    zip_safe=True,
)
