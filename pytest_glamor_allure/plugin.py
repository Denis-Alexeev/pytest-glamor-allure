from typing import TYPE_CHECKING, List
import re

from allure_commons.model2 import (
    TestAfterResult,
    TestBeforeResult,
    TestResultContainer,
)
import attr

from glamor.patches import PatchHelper
import glamor as allure
import pitest as pytest


@attr.s
class TestResultContainer(TestResultContainer):
    if TYPE_CHECKING:
        befores: List[TestBeforeResult] = []
        afters: List[TestAfterResult] = []

    glamor_setup_name: str = attr.ib(default=None)
    glamor_setup_hidden: bool = attr.ib(default=False)
    glamor_teardown_name: str = attr.ib(default=None)
    glamor_teardown_hidden: bool = attr.ib(default=False)
    glamor_scope: str = attr.ib(default=None)
    glamor_autouse: bool = attr.ib(default=False)
    glamor_afters: List[TestAfterResult] = attr.ib(factory=list)
    glamor_befores: List[TestBeforeResult] = attr.ib(factory=list)


@pytest.hookimpl(tryfirst=True)
def pytest_fixture_post_finalizer(fixturedef, request):
    listener = allure.listener
    if not listener:
        return
    container_uuid = listener._cache.get(fixturedef)
    if container_uuid is None:
        return
    container: TestResultContainer
    container = allure.reporter._items.get(container_uuid)
    if container is None:
        return

    func = fixturedef.func
    teardown_name = getattr(func, "__glamor_teardown_display_name__", None)
    teardown_hidden = getattr(
        func, "__glamor_teardown_display_hidden__", False
    )
    setup_name = getattr(func, "__glamor_setup_display_name__", None)
    setup_hidden = getattr(func, "__glamor_setup_display_hidden__", False)

    fixture_name: str = func.__name__
    fixture_func = func.__globals__[fixture_name]
    autouse: bool = fixture_func._pytestfixturefunction.autouse

    container.glamor_setup_name = setup_name
    container.glamor_setup_hidden = setup_hidden
    container.glamor_teardown_name = teardown_name
    container.glamor_teardown_hidden = teardown_hidden
    container.glamor_scope = fixturedef.scope
    container.glamor_autouse = autouse


class GlamorReportLogger:
    @allure.hookimpl(tryfirst=True, hookwrapper=True)
    def report_container(self, container: TestResultContainer):
        c = container

        if not hasattr(c, "glamor_setup_name"):
            yield
            return

        autouse = ""
        if PatchHelper.i_should_add_autouse() and c.glamor_autouse:
            autouse = "a"

        scope_before = ""
        scope_after = ""
        scope = f"[{c.glamor_scope[:1].upper()}{autouse}]"
        if PatchHelper.i_should_add_scope_before():
            scope_before = scope + " "
        elif PatchHelper.i_should_add_scope_after():
            scope_after = " " + scope

        # Handle setup name. We do not hide setup if it did not pass.
        befores_passed = {b.status for b in c.befores} == {"passed"}
        if c.glamor_setup_hidden and befores_passed:
            # Save copy in json file for debugging and testing needs
            c.glamor_befores = c.befores.copy()
            c.befores.clear()
        else:
            c.glamor_befores = []

        setup_name_is_str = isinstance(c.glamor_setup_name, str)
        for before in c.befores:
            if c.glamor_setup_name and setup_name_is_str:
                before.name = c.glamor_setup_name

            if isinstance(before.name, str):
                before.name = scope_before + before.name + scope_after

        # Handle teardown name. We do not hide teardown if it did not pass.
        afters_passed = {a.status for a in c.afters} == {"passed"}
        if c.glamor_teardown_hidden and afters_passed:
            # Save copy in json file for debugging and testing needs
            c.glamor_afters = c.afters.copy()
            c.afters.clear()
        else:
            c.glamor_afters = []

        glamor_name = c.glamor_teardown_name
        tear_name_is_str = isinstance(c.glamor_teardown_name, str)
        for after in c.afters:
            if c.glamor_teardown_name and tear_name_is_str:
                new_name = re.sub(".*(?=::)", glamor_name, after.name, 1)
                after.name = new_name
            if len(c.afters) == 1 and isinstance(after.name, str):
                if after.name.endswith("::0"):
                    after.name = after.name[:-3]
            if isinstance(after.name, str):
                after.name = scope_before + after.name + scope_after

        # Do not save redundant data into json file
        c.glamor_setup_name = None
        c.glamor_setup_hidden = None
        c.glamor_teardown_name = None
        c.glamor_teardown_hidden = None
        c.glamor_scope = None
        c.glamor_autouse = None

        # can cause heart attack. do not try to repeat.
        c.__class__ = TestResultContainer

        yield


allure.plugin_manager.register(GlamorReportLogger())
