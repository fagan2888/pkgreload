NAME = 'pkgreload'
VERSION = '0.0.1'
AUTHOR = 'Matthew W. Hoffman'
AUTHOR_EMAIL = 'mwh30@cam.ac.uk'
URL = 'http://github.com/mwhoffman/pkgreload'
DESCRIPTION = 'A simple function for reloading python packages'


from setuptools import setup


if __name__ == '__main__':
    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=DESCRIPTION,
        url=URL,
        py_modules=['pkgreload'])

