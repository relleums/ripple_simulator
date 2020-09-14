import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="ripple_simulator",
    version="0.0.0",
    description="Simulate digital signal propagation",
    long_description=long_description,
    url="https://github.com/relleums/ripple_simulator",
    author="Sebastian Achim Mueller",
    author_email="sebastian-achim.mueller@mpi-hd.mpg.de",
    license="GPLv3",
    packages=["ripple_simulator",],
    package_data={"ripple_simulator": ["tests/resources/*",]},
    install_requires=["xmltodict"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
    ],
)
