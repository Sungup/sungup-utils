import setuptools
import unittest

# ==================================================
# Package information
# ==================================================
NAME = 'sglove-utils'
AUTHOR = 'Sungup Moon'
VERSION = '0.0.1'
EMAIL = 'sungup@me.com'
LICENSE = 'MIT'
DESCRIPTION = 'Personal utility modules.'
URL = 'https://github.com/Sungup/sglove-utils'
DOWNLOAD_URL = '{url}/archive/v{ver}.tar.gz'.format(url=URL, ver=VERSION)
KEYWORDS = ['python', 'automation', 'CLI']


LONG_DESCRIPTION = open('README.md', 'r').read()

ENTRY_POINTS = {}

PACKAGES = setuptools.find_packages(
    exclude=['temp']
)

INSTALL_REQUIRES = []

EXTRAS_REQUIRE = {}

TEST_SUITE = 'setup.test_suite'


# ==================================================
# Unit test
# ==================================================
def test_suite():
    _loader = unittest.TestLoader()
    _suite = _loader.discover('tests', pattern='test_*.py')

    return _suite


# ==================================================
# Utilities
# ==================================================
if __name__ == '__main__':
    setuptools.setup(
        name=NAME,
        author=AUTHOR,
        version=VERSION,
        author_email=EMAIL,
        license=LICENSE,
        description=DESCRIPTION,
        url=URL,
        download_url=DOWNLOAD_URL,
        long_description=LONG_DESCRIPTION,
        extras_require=EXTRAS_REQUIRE,
        install_requires=INSTALL_REQUIRES,
        test_suite=TEST_SUITE,
        packages=PACKAGES,
        include_package_data=True,
        zip_safe=False,
        entry_points=ENTRY_POINTS
    )
