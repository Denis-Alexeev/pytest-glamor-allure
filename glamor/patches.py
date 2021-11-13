from __future__ import annotations

from types import MethodType
from typing import TYPE_CHECKING, Optional
import inspect
import logging
import os

from allure import dynamic as allure_dynamic, title as allure_title
from allure_commons._allure import StepContext

if TYPE_CHECKING:
    from typing import Literal

    from _pytest.fixtures import Config, FixtureFunctionMarker
    from allure_pytest.listener import AllureListener, AllureReporter

    class FixtureFunction:
        _pytestfixturefunction: FixtureFunctionMarker


class PatchHelper:
    _add_scope_before_name: bool = None
    _add_scope_after_name: bool = None
    _add_autouse: bool = None

    @classmethod
    def include_scope_before_titles(cls):
        cls._add_scope_after_name = False
        cls._add_scope_before_name = True

    @classmethod
    def include_scope_after_titles(cls):
        cls._add_scope_after_name = True
        cls._add_scope_before_name = False

    @classmethod
    def include_autouse_in_titles(cls):
        cls._add_autouse = True

    @classmethod
    def exclude_autouse_from_titles(cls):
        cls._add_autouse = False

    @classmethod
    def i_should_add_scope_before(cls) -> bool:
        return cls._add_scope_before_name

    @classmethod
    def i_should_add_scope_after(cls) -> bool:
        return cls._add_scope_after_name

    @classmethod
    def i_should_add_autouse(cls) -> bool:
        return cls._add_autouse

    @staticmethod
    def extract_real_func(func):
        if getattr(func, "__pytest_wrapped__", None):
            return func.__pytest_wrapped__.obj
        return func

    @staticmethod
    def __raise_if_not_fixture(fixture: "FixtureFunction"):
        error_message = (
            "dynamic.title.setup and dynamic.title.teardown "
            "must be used only inside fixture"
        )
        try:
            return fixture._pytestfixturefunction
        except AttributeError:
            raise RuntimeError(error_message)

    @classmethod
    def get_real_function_of_fixture(cls, current_frame):
        fixture_frame = current_frame.f_back
        fixture_name = fixture_frame.f_code.co_name
        fixture_func = fixture_frame.f_globals[fixture_name]
        cls.__raise_if_not_fixture(fixture_func)
        return cls.extract_real_func(fixture_func)


class Title:
    def __call__(self, test_title: str):
        return allure_title(test_title)

    @staticmethod
    def setup(setup_title: str = None, *, hidden=False):
        def decorator(func):
            function = PatchHelper.extract_real_func(func)
            function.__glamor_setup_display_name__ = setup_title
            function.__glamor_setup_display_hidden__ = hidden
            return func

        return decorator

    @staticmethod
    def teardown(teardown_title: str = None, *, hidden=False):
        def decorator(func):
            function = PatchHelper.extract_real_func(func)
            function.__glamor_teardown_display_name__ = teardown_title
            function.__glamor_teardown_display_hidden__ = hidden
            return func

        return decorator


class DynamicFixtureTitle:
    def __call__(self, test_title: str):
        return allure_dynamic.title(test_title)

    @staticmethod
    def setup(setup_title: str = None, *, hidden: bool = None):
        func = PatchHelper.get_real_function_of_fixture(inspect.currentframe())
        if setup_title:
            func.__glamor_setup_display_name__ = setup_title
        if isinstance(hidden, bool):
            func.__glamor_setup_display_hidden__ = hidden

    @staticmethod
    def teardown(teardown_title: str = None, *, hidden: bool = None):
        func = PatchHelper.get_real_function_of_fixture(inspect.currentframe())
        if teardown_title:
            func.__glamor_teardown_display_name__ = teardown_title
        if isinstance(hidden, bool):
            func.__glamor_teardown_display_hidden__ = hidden


class Dynamic(allure_dynamic):
    title = DynamicFixtureTitle()


def indent_output(indent: bool, override=False):
    key_name = "ALLURE_INDENT_OUTPUT"
    if override and not indent:
        os.environ.pop(key_name, None)
        return
    os.environ[key_name] = "True"
    return


def include_scope_in_title(where: 'Literal["before", "after"]', autouse=False):
    if getattr(include_scope_in_title, "called", False):
        raise RuntimeError("include_scope can be called only once per runtime")
    if where == "before":
        PatchHelper.include_scope_before_titles()
    elif where == "after":
        PatchHelper.include_scope_after_titles()
    else:
        raise RuntimeError('"where" argument must be "before" or "after"')

    if autouse:
        PatchHelper.include_autouse_in_titles()
    include_scope_in_title.called = True


def logging_allure_steps(logger: Optional[logging.Logger], level: int = 21):

    allure_enter: MethodType = getattr(
        logging_allure_steps, "allure_enter", StepContext.__enter__
    )
    logging_allure_steps.allure_enter = allure_enter
    if logger is not None and not isinstance(logger, logging.Logger):
        raise RuntimeError('"logger" must be instance of Logger or NoneType')
    if logger is None:
        StepContext.__enter__ = allure_enter
        return

    logging.addLevelName(level, "STEP")

    def patched_enter(self: StepContext):
        if self.title:
            logger.log(level, self.title)
        return allure_enter(self)

    StepContext.__enter__ = patched_enter


title = Title()
pytest_config: Optional["Config"] = None
listener: Optional["AllureListener"] = None
reporter: Optional["AllureReporter"] = None
