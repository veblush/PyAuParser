from distutils.core import setup

setup(
    name='PyAuParser',
    version='0.5',
    author="Esun Kim",
    author_email='veblush+git_at_gmail.com',
    url='https://github.com/veblush/PyAuParser',
    description="New python engine for GOLD Parser",
    license='MIT',
    packages=['pyauparser', 'pyauparser.test'],
    package_dir={'pyauparser.test': 'pyauparser/test'},
    package_data={'pyauparser.test': ['data/*']},
    scripts=["scripts/auparser.py"],
)
