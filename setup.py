from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(
	name='ckanext-dgvat_xls',
	version=version,
	description="data.gv.at plugin to export datasets to .xls",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='ckan, xls, export, datasets',
	author='BRZ GmbH',
	author_email='data@brz.gv.at',
	url='http://www.brz.gv.at',
	license='GPL',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.dgvat_xls'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
    [ckan.plugins]
	dgvat_xls = ckanext.dgvat_xls.plugin:DgvatXlsExport
	""",
)
