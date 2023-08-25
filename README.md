# pytest-glamor-allure

pytest plugin extending allure behaviour

---

![](https://github.com/Denis-Alexeev/pytest-glamor-allure/actions/workflows/python-publish.yml/badge.svg)
![](https://github.com/Denis-Alexeev/pytest-glamor-allure/actions/workflows/run_lint_and_tests.yml/badge.svg)
![](https://github.com/Denis-Alexeev/pytest-glamor-allure/actions/workflows/codeql-analysis.yml/badge.svg)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytest-glamor-allure)](https://pypi.org/project/pytest-glamor-allure/)
[![PyPI](https://img.shields.io/pypi/v/pytest-glamor-allure)](https://pypi.org/project/pytest-glamor-allure/)
[![PyPI - Status](https://img.shields.io/pypi/status/pytest-glamor-allure)](https://pypi.org/project/pytest-glamor-allure/)
[![Downloads](https://static.pepy.tech/badge/pytest-glamor-allure)](https://pepy.tech/project/pytest-glamor-allure)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linter: flake8](https://img.shields.io/badge/linter-flake8-blue)](https://pypi.org/project/flake8/)


1. [Why has it been created?](#why_created)
2. [What is it?](#what_it_is)
3. [Why is it named "glamor"?](#name_glamor)
4. [How to install?](#installation)
5. [What does it can?](#what_does_it_can)
   * [Fancy names for setups and teardowns](#fancy_names)
   * [Hide setup and teardown](#hide_fixture)
   * [Display 'scope' and 'autouse' parameters in fixture title](#display_scope)
   * [No more '::0' in teardown title](#no_more_ending)
   * [Add allure.step titles into logging](#logging_step)
   * [What else?](#what_else)
6. [Pleasant bonus 🎁](#pleasant_bonus)
7. [How can I help?](#how_help)

## Why has it been created?<a id="why_created"></a>

Just because [allure-python](https://github.com/allure-framework/allure-python) plugin accepts PRs very slowly. Sad but true.

I want to inject more functionality into it. That's why I've decided to create this plugin.

## What is it?<a id="what_it_is"></a>

As been said it is pytest plugin (tnx captain 😄). Consider this plugin just as some extension for [allure-pytest](https://github.com/allure-framework/allure-python/tree/master/allure-pytest).

Hopefully, they'll see this code and add some of this functionality later.

## Why is it named "glamor"?<a id="name_glamor"></a>

Because "glamor" is a synonym for "allure". Glamor does the same thing as allure-pytest does but a little more.

The main idea is to just replace imports in you project: instead of `import allure` you type `import glamor as allure` and everything works as before.

## How to install?<a id="installation"></a>

```shell
pip install pytest-glamor-allure
````

That's it.

## What does it can?<a id="what_does_it_can"></a>

It's the most interesting part of the ReadMe.

### Fancy names for setups and teardowns<a id="fancy_names"></a>

[allure-python](https://github.com/allure-framework/allure-python) provides possibility to set title for fixture with `@allure.title` decorator.

But there is no chance to set different titles for setup and teardown.
Glamor does can this!

```python
import pytest
import glamor as allure

@pytest.fixture
@allure.title.setup('Fancy setup name')
@allure.title.teardown('Fancy teardown name')
def fixture():
    yield

@allure.title('Test Title')
def test_test(fixture):
    with allure.step('test step'):
        pass
```

![image](https://raw.githubusercontent.com/Denis-Alexeev/pytest-glamor-allure/master/assets/fancy_titles.png)

And moreover. You can dynamically change setup and teardown titles for fixtures.

***Only one restriction:*** dynamic hook must be used inside the fixture's body.

```python
import pytest
import glamor as allure


@pytest.fixture
def fixture():
    yield
    allure.dynamic.title.setup('Fancy dynamic setup name')
    allure.dynamic.title.teardown('Fancy dynamic teardown name')


@allure.title('Test Title')
def test_test(fixture):
    with allure.step('test step'):
        pass
```

![image](https://raw.githubusercontent.com/Denis-Alexeev/pytest-glamor-allure/master/assets/fancy_dynamic_titles.png)

### Hide setup and teardown<a id="hide_fixture"></a>

Have you ever wanted to conceal setup and/or teardown from 'allure' report?

Well, now you can.

```python
import pytest
import glamor as allure


@pytest.fixture
@allure.title.setup(hidden=True)
@allure.title.teardown('Teardown ONE')
def fixture():
    yield


@pytest.fixture
@allure.title.setup('Setup TWO')
def fixture2():
    yield

    if True:
        allure.dynamic.title.teardown(hidden=True)


@allure.title('Test Title')
def test_test(fixture, fixture2):
    with allure.step('test step'):
        pass
```

![image](https://raw.githubusercontent.com/Denis-Alexeev/pytest-glamor-allure/master/assets/hide_fixture.png)

But! If any exception (including `Skipped`) is raised, then hidden setups and teardowns are shown forcefully.

```python
import pytest
import glamor as allure


@pytest.fixture
@allure.title.setup('Setup is displayed in case of failure', hidden=True)
@allure.title.teardown('Teardown ONE')
def fixture():
    with allure.step('fail step'):
        assert False, 'some exception in setup'
    yield


@pytest.fixture
@allure.title.setup('Setup TWO')
def fixture2():
    yield

    if True:
        allure.dynamic.title.teardown(hidden=True)
    pytest.skip('we decided to skip')


@allure.title('Test Title')
def test_test(fixture2, fixture):
    with allure.step('test step'):
        pass
```

![image](https://raw.githubusercontent.com/Denis-Alexeev/pytest-glamor-allure/master/assets/hide_fixture_failure.png)

### Display 'scope' and 'autouse' fixture parameters in fixture title<a id="display_scope"></a>

Sometimes it is useful to know which scope this fixture is, and was it called manually or autoused.

Just call the function once per runtime `include_scope_in_title` before pytest starts execution of any hook (during modules initialization).

```python
import pytest
import glamor as allure

allure.include_scope_in_title('before', autouse=True)


@pytest.fixture(scope='session', autouse=True)
@allure.title.setup('Fancy setup name')
def fixture():
    yield


@pytest.fixture
@allure.title.setup('Setup TWO')
def fixture2():
    yield


@allure.title('Test Title')
def test_test(fixture2):
    with allure.step('test step'):
        pass
```

![image](https://github.com/Denis-Alexeev/pytest-glamor-allure/raw/master/assets/scope_before.png)

The big letter is the first letter of the scope name (one of 'function', 'class', 'module', 'package', 'session'). The lower letter 'a' says that fixture was autoused.

If you want to put this information to the end of the title, then just call the function as `allure.include_scope_in_title('after', autouse=True)` and you get:

![image](https://raw.githubusercontent.com/Denis-Alexeev/pytest-glamor-allure/master/assets/scope_after.png)

### No more '::0' in teardown title<a id="no_more_ending"></a>

Have you noticed '::0' in raw teardown titles? No? That's because glamor strips such ending if fixture has not more than one finalizer.

### Add allure.step titles into logging<a id="logging_step"></a>

Have you ever tried to understand when the particular allure step started looking at tests' logs? Of course, you have!

With "glamor" you can register you own logger, which is considered to print steps' titles into output.

```python
import logging
import sys
import glamor as allure


# Create logger
logger = logging.getLogger('MyLogger')
logger.setLevel(logging.INFO)

fmt = logging.Formatter('[%(levelname)s] %(message)s')

handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(fmt)

logger.addHandler(handler)

# Register logger in allure
allure.logging_allure_steps(logger)


# Execute tests' code
logger.info("start message")

with allure.step("step message"):
    pass

logger.error("end message")
```

```shell
[INFO] start message
[STEP] step message
[ERROR] end message
```

`logging_allure_steps` should be called only once - during modules initialization. But who am I to restrict you?

If you need you can turn off this behaviour by calling the function with `None` instead of `logging.Logger` instance.

### What else?<a id="what_else"></a>

```python
import glamor as allure

allure.listener  # access to AllureListener plugin instance
allure.reporter  # alias for allure.listener.allure_logger
allure.pytest_config  # access to pytest.Config instance. alias for allure.listener.config
```

Also via 'glamor' module you get direct access to many objects from:

* allure_commons
* allure_commons._allure
* allure_commons.model2
* allure_commons.types
* allure_commons.utils
* allure_pytest.utils

## Pleasant bonus 🎁<a id="pleasant_bonus"></a>

Type `import pitest as pytest` instead of `import pytest` and get direct access to a bunch of objects from `pytest` and `_pytest` modules.

## How can I help?<a name="how_help"></a>

Your contribution is highly appreciated. Please read [CONTRIBUTING.md](https://github.com/Denis-Alexeev/pytest-glamor-allure/blob/master/CONTRIBUTING.md) before you start.
