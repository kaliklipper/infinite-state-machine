import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-state-machine-kaliklipper",
    version="0.1.2",
    author="kaliklipper",
    author_email="kaliklipper@gmail.com",
    description="An Infinite State Machine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kaliklipper/python-state-machine",
    packages=setuptools.find_packages(),
    package_data={'ism.core': ['*.json'], 'ism.tests.test_action_pack': ['*.json']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
