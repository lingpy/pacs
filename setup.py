from setuptools import setup, find_packages


setup(
    name='pacs',
    version='0.1',
    description="Creating partial colexifications from CLDF datasets.",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author='Johann-Mattis List',
    author_email='mattis.list@lingpy.org',
    url='https://github.com/lingpy/pacs',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[
        "lingpy",
        "cltoolkit",
        'attrs>=18.1',
        'pyglottolog>=2.0',
        'python-igraph>=0.7.1',
        'networkx>=2.1',  # We rely on the `node` attribute
    ],
    extras_require={
        'dev': [
            'tox',
            'flake8',
            'wheel',
            'twine',
        ],
        'test': [
            'pytest>=5.0',
            'pytest-cov',
            'pytest-mock',
            'coverage>=4.2',
        ],
    },

)
