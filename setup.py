from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='americano',
    version='0.0.0',
    packages=['americano'],
    license='MIT',
    install_requires=['six'],
    long_description=readme(),
    author_email='jungroth@gmail.com',
    author='Travis Jungroth',
    url='http://github.com/travisjungroth/americano',
)
