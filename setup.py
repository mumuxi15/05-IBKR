from setuptools import setup, find_packages

setup(
	name='local_package',
	version='0.1',
	packages=find_packages(exclude=['tests*']),
	license='MIT',
	description='panini use only',
	long_description=open('README.md').read(),
	install_requires=['numpy'],
	author='panini',
	author_email='myemail@example.com'
)
