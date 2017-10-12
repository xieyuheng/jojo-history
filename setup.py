from setuptools import setup, find_packages

with open('README') as f:
    readme = f.read()

with open('LICENSE/LICENSE-of-xieyuheng') as f:
    license = f.read()

setup(
    name='jojo',
    version='0.0.7',
    description="jojo's programming adventure in python",
    url='http://github.com/xieyuheng/jojo-on-python',

    author='xieyuheng',
    author_email='xyheme@gmail.com',

    py_modules=['jojo'],
    scripts=['jojo'],
    packages=find_packages(exclude=('tests', 'docs'))

    long_description=readme,
    license=license,
)
