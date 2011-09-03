import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.markdown')

setup(
    name = "django-galleries",
    version = "0.1",
    description='Simple Djagno galleries.',
    long_description=README,

    author = 'Matthew Tretter',
    author_email = 'matthew@exanimo.com',
    packages = [
        'galleries',
        'exampleapp',
    ],
    install_requires = [
        'django-imagekit>=0.3.6', # TODO: Relax this requirement a bit. I'm sure it works with a much earlier version.
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)