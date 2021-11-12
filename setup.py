from setuptools import setup

setup(
    version="0.0.1",
    name="pytest_glamor_allure",
    packages=["pytest_glamor_allure", "glamor"],
    entry_points={
        "pytest11": ["pytest_glamor_allure = pytest_glamor_allure.plugin"]
    },
    classifiers=["Framework :: Pytest"],
    install_requires=[
        "allure-pytest",
        "allure-python-commons",
        "pytest",
        "attrs",
    ],
    py_modules=["glamor", "pytest_glamor_allure", "pitest"],
    python_requires=">=3.7",
)
