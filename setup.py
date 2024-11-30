import os
import warnings

from setuptools import find_namespace_packages, setup

BASE_PATH = os.path.dirname(__file__)


def find_version():
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    if not os.path.exists("version.txt"):
        return "0.0.1"
    with open("version.txt", "r") as f:
        content = f.read().strip()
        if len(content) == 0:
            return "0.0.1"
        return content


__version__ = find_version()


def main():
    try:
        with open('requirements.txt') as req_file:
            requirements = req_file.read().splitlines()
    except FileNotFoundError:
        requirements = []
        warnings.warn('Requirements file absents, requirements will be set to empty list')

    setup(
        name='file_manager',
        version=__version__,
        description="Tool for uploading files",
        python_requires='>=3.8',
        packages=find_namespace_packages(include=['app.*', 'app']),
        include_package_data=True,
        install_requires=requirements,
        entry_points={
            'console_scripts': [
                'file_manager=app:run_server',
            ]
        },
    )


if __name__ == "__main__":
    main()
