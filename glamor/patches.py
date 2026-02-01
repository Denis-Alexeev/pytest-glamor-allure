from __future__ import annotations

from types import FrameType, MethodType
from typing import TYPE_CHECKING, Callable, cast
import inspect
import logging

from allure import dynamic as allure_dynamic, title as allure_title

if TYPE_CHECKING:
    from typing import Literal

    from _pytest.fixtures import (
        Config,  # type: ignore[reportPrivateImportUsage]
        FixtureDef,
        FixtureManager,
    )
    from allure_pytest.listener import AllureListener, AllureReporter


class PatchHelper:
    """Helper class to store patching configuration and methods."""

    _add_scope_before_name: bool | None = None
    _add_scope_after_name: bool | None = None
    _add_autouse: bool | None = None
    fixt_mgr: FixtureManager | None = None
    logger: logging.Logger | None = None
    level: int = 21

    @classmethod
    def include_scope_before_titles(cls) -> None:
        """Enable adding scope to titles of fixtures."""
        cls._add_scope_after_name = False
        cls._add_scope_before_name = True

    @classmethod
    def include_scope_after_titles(cls) -> None:
        """Enable adding scope to titles of fixtures."""
        cls._add_scope_after_name = True
        cls._add_scope_before_name = False

    @classmethod
    def include_autouse_in_titles(cls) -> None:
        """Enable adding 'a' letter to titles of autouse fixtures."""
        cls._add_autouse = True

    @classmethod
    def i_should_add_scope_before(cls) -> bool | None:
        """Check whether scope should be added to titles or not."""
        return cls._add_scope_before_name

    @classmethod
    def i_should_add_scope_after(cls) -> bool | None:
        """Check whether scope should be added to titles or not."""
        return cls._add_scope_after_name

    @classmethod
    def i_should_add_autouse(cls) -> bool | None:
        """Check whether autouse should be added to titles or not."""
        return cls._add_autouse

    @staticmethod
    def extract_real_func(func: Callable) -> Callable:
        """Extract real function from pytest wrapper."""
        if hasattr(func, '_get_wrapped_function'):  # pytest >= 8.4
            return func._get_wrapped_function()
        if getattr(func, '__pytest_wrapped__', None):  # pytest < 8.4
            return func.__pytest_wrapped__.obj
        return func

    @classmethod
    def fixture_has_autouse(cls, fixturedef: FixtureDef) -> bool:
        """Check whether fixture is autouse or not."""
        autos = cast('FixtureManager', cls.fixt_mgr)._nodeid_autousenames.get(
            fixturedef.baseid,
            [],
        )
        return fixturedef.argname in autos

    @classmethod
    def get_real_function_of_fixture(
        cls,
        current_frame: FrameType,
    ) -> Callable:
        """Get real function object of fixture from current frame."""
        fixture_frame = cast('FrameType', current_frame.f_back)
        fixture_name = fixture_frame.f_code.co_name
        fixturedefs = cast(
            'FixtureManager',
            cls.fixt_mgr,
        )._arg2fixturedefs.get(fixture_name, [])
        if not fixturedefs:
            msg = f'there is no fixture named "{fixture_name}"'
            raise RuntimeError(msg)
        for fixturedef in fixturedefs:
            fixture_func = fixturedef.func
            func = cls.extract_real_func(fixture_func)
            if func.__code__ == fixture_frame.f_code:
                if isinstance(func, MethodType):
                    func = func.__func__
                return func
        msg = 'Unknown error during "dynamic.title"'
        raise RuntimeError(msg)


class Title(Callable):  # type: ignore[reportGeneralTypeIssues]
    """Replacement for allure.title."""

    def __call__(self, test_title: str) -> Callable[[Callable], Callable]:
        """As usual @allure.title(...) signature.

        :param test_title: title for fixture or test
        """
        return allure_title(test_title)

    @staticmethod
    def setup(
        setup_title: str | None = None,
        *,
        hidden: bool = False,
    ) -> Callable[[Callable], Callable]:
        """Replace standard fixture name with fancy setup name.

        If setup fails it is always displayed. In spite of "hidden=True".

        :param setup_title: title to use in setup for this fixture
        :param hidden: whether setup should be displayed or not
        """

        def decorator(func: Callable) -> Callable:
            function = PatchHelper.extract_real_func(func)
            function.__glamor_setup_display_name__ = setup_title
            function.__glamor_setup_display_hidden__ = hidden
            return func

        return decorator

    @staticmethod
    def teardown(
        teardown_title: str | None = None,
        *,
        hidden: bool = False,
    ) -> Callable[[Callable], Callable]:
        """Replace standard fixture name with fancy teardown name.

        If teardown fails it is always displayed. In spite of "hidden=True".

        :param teardown_title: title to use in teardown for this fixture
        :param hidden: whether teardown should be displayed or not
        """

        def decorator(func: Callable) -> Callable:
            function = PatchHelper.extract_real_func(func)
            function.__glamor_teardown_display_name__ = teardown_title
            function.__glamor_teardown_display_hidden__ = hidden
            return func

        return decorator


class DynamicFixtureTitle:
    """Replacement for allure.dynamic.title."""

    def __call__(self, test_title: str) -> Callable[[Callable], Callable]:
        """As usual allure.dynamic.title(...) signature.

        :param test_title: title for test to set dynamically
        """
        return allure_dynamic.title(test_title)  # type: ignore[reportReturnType]

    @staticmethod
    def setup(
        setup_title: str | None = None,
        *,
        hidden: bool | None = None,
    ) -> None:
        """Dynamically replace standard fixture name with fancy setup name.

        If setup fails it is always displayed. In spite of "hidden=True".
        Can be used only inside fixture body.

        :param setup_title: title to use in setup for this fixture
        :param hidden: whether setup should be displayed or not
        """
        func = PatchHelper.get_real_function_of_fixture(
            cast('FrameType', inspect.currentframe()),
        )
        if setup_title:
            func.__glamor_setup_display_name__ = setup_title
        if isinstance(hidden, bool):
            func.__glamor_setup_display_hidden__ = hidden

    @staticmethod
    def teardown(
        teardown_title: str | None = None,
        *,
        hidden: bool | None = None,
    ) -> None:
        """Dynamically replace standard fixture name with fancy teardown name.

        If teardown fails it is always displayed. In spite of "hidden=True".
        Can be used only inside fixture body.

        :param teardown_title: title to use in teardown for this fixture
        :param hidden: whether teardown should be displayed or not
        """
        func = PatchHelper.get_real_function_of_fixture(
            cast('FrameType', inspect.currentframe()),
        )
        if teardown_title:
            func.__glamor_teardown_display_name__ = teardown_title
        if isinstance(hidden, bool):
            func.__glamor_teardown_display_hidden__ = hidden


class Dynamic(allure_dynamic):
    """Replacement for allure.dynamic."""

    title = DynamicFixtureTitle() # type: ignore[reportAssignmentType]


def include_scope_in_title(
    where: Literal["before", "after"],
    autouse: bool = False,  # noqa: FBT001, FBT002
) -> None:
    """Print scope and autouse before or after fixture title.

    Example: "[Sa] session_fixture_name" or "class_fixture_name [C]".
    Can be invoked only once per runtime.

    :param where: where to print - "before" title or "after"
    :param autouse: whether to include "a" letter or not
    """
    if getattr(include_scope_in_title, 'called', False):
        msg = 'include_scope can be called only once per runtime'
        raise RuntimeError(msg)
    if where == 'before':
        PatchHelper.include_scope_before_titles()
    elif where == 'after':
        PatchHelper.include_scope_after_titles()
    else:
        msg = '"where" argument must be "before" or "after"'
        raise RuntimeError(msg)

    if autouse:
        PatchHelper.include_autouse_in_titles()
    include_scope_in_title.called = True


def logging_allure_steps(
    logger: logging.Logger | None,
    level: int = 21,
) -> None:
    """Print allure.step titles in stdout logging.

    If logger is None - stops printing allure.step titles.
    Can be invoked as many times as you need.

    :param logger: instance of `logging.Logger` or None
    :param level: level for logging. Default 21 (between INFO and WARNING)
    """
    if logger is not None and not isinstance(logger, logging.Logger):
        msg = '"logger" must be instance of Logger or NoneType'
        raise RuntimeError(msg)

    if not isinstance(level, int):
        msg = '"level" must be integer'
        raise TypeError(msg)

    PatchHelper.logger = logger
    PatchHelper.level = level
    logging.addLevelName(level, 'STEP')


title = Title()
pytest_config: Config | None = None
listener: AllureListener | None = None
reporter: AllureReporter | None = None
