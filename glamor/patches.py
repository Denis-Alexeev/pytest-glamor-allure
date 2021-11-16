from __future__ import annotations

from types import MethodType
from typing import TYPE_CHECKING, Callable, Optional
import inspect
import logging

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


class Title(Callable):
    def __call__(self, test_title: str) -> Callable[[Callable], Callable]:
        """As usual @allure.title(...) signature

        :param test_title: title for fixture or test
        """
        return allure_title(test_title)

    @staticmethod
    def setup(
        setup_title: str = None,
        *,
        hidden=False,
    ) -> Callable[[Callable], Callable]:
        """Replace standard fixture name with fancy setup name.
        If setup fails it is always displayed. In spite of "hidden=True".

        :param setup_title: title to use in setup for this fixture
        :param hidden: whether setup should be displayed or not
        """

        def decorator(func):
            function = PatchHelper.extract_real_func(func)
            function.__glamor_setup_display_name__ = setup_title
            function.__glamor_setup_display_hidden__ = hidden
            return func

        return decorator

    @staticmethod
    def teardown(
        teardown_title: str = None,
        *,
        hidden=False,
    ) -> Callable[[Callable], Callable]:
        """Replace standard fixture name with fancy teardown name.
        If teardown fails it is always displayed. In spite of "hidden=True".

        :param teardown_title: title to use in teardown for this fixture
        :param hidden: whether teardown should be displayed or not
        """

        def decorator(func):
            function = PatchHelper.extract_real_func(func)
            function.__glamor_teardown_display_name__ = teardown_title
            function.__glamor_teardown_display_hidden__ = hidden
            return func

        return decorator


class DynamicFixtureTitle:
    def __call__(self, test_title: str) -> Callable[[Callable], Callable]:
        """As usual allure.dynamic.title(...) signature

        :param test_title: title for test to set dynamically
        """
        return allure_dynamic.title(test_title)

    @staticmethod
    def setup(setup_title: str = None, *, hidden: bool = None):
        """Dynamically replace standard fixture name with fancy setup name.
        If setup fails it is always displayed. In spite of "hidden=True".
        Can be used only inside fixture body.

        :param setup_title: title to use in setup for this fixture
        :param hidden: whether setup should be displayed or not
        """
        func = PatchHelper.get_real_function_of_fixture(inspect.currentframe())
        if setup_title:
            func.__glamor_setup_display_name__ = setup_title
        if isinstance(hidden, bool):
            func.__glamor_setup_display_hidden__ = hidden

    @staticmethod
    def teardown(teardown_title: str = None, *, hidden: bool = None):
        """Dynamically replace standard fixture name with fancy teardown name.
        If teardown fails it is always displayed. In spite of "hidden=True".
        Can be used only inside fixture body.

        :param teardown_title: title to use in teardown for this fixture
        :param hidden: whether teardown should be displayed or not
        """
        func = PatchHelper.get_real_function_of_fixture(inspect.currentframe())
        if teardown_title:
            func.__glamor_teardown_display_name__ = teardown_title
        if isinstance(hidden, bool):
            func.__glamor_teardown_display_hidden__ = hidden


class Dynamic(allure_dynamic):
    """Replacement for allure.dynamic."""

    title = DynamicFixtureTitle()


def include_scope_in_title(where: 'Literal["before", "after"]', autouse=False):
    """Print scope and autouse before or after fixture title.
    Example: "[Sa] session_fixture_name" or "class_fixture_name [C]".
    Can be invoked only once per runtime.

    :param where: where to print - "before" title or "after"
    :param autouse: whether to include "a" letter or not
    """
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
    """Print allure.step titles in stdout logging.
    If logger is None - stops printing allure.step titles.
    Can be invoked as many times as you need.

    :param logger: instance of `logging.Logger` or None
    :param level: level for logging. Default 21 (between INFO and WARNING)
    """

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
