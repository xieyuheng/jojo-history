from setuptools import setup

with open('README') as f:
    readme = f.read()

setup(
    name='jojo',
    version='0.0.23',
    description="jojo's programming adventure in python",
    url='http://github.com/xieyuheng/jojo-on-python',

    author='xieyuheng',
    author_email='xyheme@gmail.com',


    packages=['jojo'],
    package_data={'jojo': ['*.jo']},
    scripts=['bin/jojo'],
    python_requires='>=3',

    long_description=readme,
    license="I dedicate all my works here to all human beings.",
)
