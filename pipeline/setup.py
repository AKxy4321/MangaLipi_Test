from setuptools import setup, find_packages

setup(
    name='MangaLipi_Test',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # Add your project's dependencies here
        # e.g., 'numpy', 'pandas', 'requests'
    ],
    entry_points={
        'console_scripts': [
            # Add command line scripts here
            # e.g., 'mangalipi=mangalipi.cli:main'
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A brief description of your project',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/MangaLipi_Test',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)