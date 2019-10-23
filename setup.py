from setuptools import setup, find_packages
setup(
    name='ConsensusTableUploader',
    version='1.0',
    packages=find_packages(),
    install_requires=['molgenis-py-client>=2.1.0', 'progressbar2==3.39.3', 'termcolor==1.1.0', 'yaspin==0.14.3', 'pandas'],
    author='Mariska Slofstra',
    license='GNU Lesser General Public License 3.0',
    test_suite='nose.collector',
    tests_require=['nose', 'parameterized']
)