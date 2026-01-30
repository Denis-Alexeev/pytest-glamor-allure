from setuptools import setup

with open('README.md') as readme:
    long_description = readme.read()

classifiers = [
    'Framework :: Pytest',
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: Russian',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'Programming Language :: Python :: 3.14',
    'Topic :: Software Development :: Testing',
    'Topic :: Software Development :: Quality Assurance',
]

install_requires = [
    'allure-pytest<=2.15.3',
    'allure-python-commons',
    'pytest<=9.0.2',
    'attrs<=25.4.0',
]

entry_points = {
    'pytest11': [
        'pytest_glamor_allure = pytest_glamor_allure.plugin',
    ],
}

if __name__ == '__main__':
    setup(
        name='pytest_glamor_allure',
        description='Extends allure-pytest functionality',
        long_description=long_description,
        long_description_content_type='text/markdown',
        author='Denis Alexeev',
        author_email='github.com@alexeev.ws',
        maintainer='Denis Alexeev',
        maintainer_email='github.com@alexeev.ws',
        url='https://github.com/Denis-Alexeev/pytest-glamor-allure',
        packages=['pytest_glamor_allure', 'glamor'],
        py_modules=['glamor', 'pytest_glamor_allure', 'pitest'],
        classifiers=classifiers,
        licence='MIT',
        setup_requires=['setuptools_scm'],
        install_requires=install_requires,
        entry_points=entry_points,
        python_requires='>=3.8',
    )
