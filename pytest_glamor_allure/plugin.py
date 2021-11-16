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
        if not hasattr(container, "glamor_setup_name"):
            yield
            return

        scope_before, scope_after = self.handle_scope(container)

        self.handle_hidden_setup(container)

        self.handle_setup_name(container, scope_before, scope_after)

        self.handle_hidden_teardown(container)

        self.handle_teardown_name(container, scope_before, scope_after)

        self.clean_redundant_fields(container)

        container.__class__ = TestResultContainer

        yield

    @staticmethod
    def handle_scope(container: TestResultContainer):
        autouse = ""
        if PatchHelper.i_should_add_autouse() and container.glamor_autouse:
            autouse = "a"

        scope_before = ""
        scope_after = ""
        scope = f"[{container.glamor_scope[:1].upper()}{autouse}]"
        if PatchHelper.i_should_add_scope_before():
            scope_before = scope + " "
        elif PatchHelper.i_should_add_scope_after():
            scope_after = " " + scope

        return scope_before, scope_after

    @staticmethod
    def handle_hidden_setup(container: TestResultContainer):
        befores_passed = {b.status for b in container.befores} == {"passed"}
        if container.glamor_setup_hidden and befores_passed:
            # Save copy in json file for debugging and testing needs
            container.glamor_befores = container.befores.copy()
            container.befores.clear()
        else:
            container.glamor_befores = []

    @staticmethod
    def handle_setup_name(
        container: TestResultContainer,
        scope_before: str,
        scope_after: str,
    ):
        setup_name_is_str = isinstance(container.glamor_setup_name, str)
        for before in container.befores:
            if container.glamor_setup_name and setup_name_is_str:
                before.name = container.glamor_setup_name

            if isinstance(before.name, str):
                before.name = scope_before + before.name + scope_after

    @staticmethod
    def handle_hidden_teardown(container: TestResultContainer):
        afters_passed = {a.status for a in container.afters} == {"passed"}
        if container.glamor_teardown_hidden and afters_passed:
            # Save copy in json file for debugging and testing needs
            container.glamor_afters = container.afters.copy()
            container.afters.clear()
        else:
            container.glamor_afters = []

    @staticmethod
    def handle_teardown_name(
        container: TestResultContainer,
        scope_before: str,
        scope_after: str,
    ):

        glamor_name = container.glamor_teardown_name
        tear_name_is_str = isinstance(container.glamor_teardown_name, str)
        for after in container.afters:
            if container.glamor_teardown_name and tear_name_is_str:
                new_name = re.sub(".*(?=::)", glamor_name, after.name, 1)
                after.name = new_name
            if len(container.afters) == 1 and isinstance(after.name, str):
                if after.name.endswith("::0"):
                    after.name = after.name[:-3]
            if isinstance(after.name, str):
                after.name = scope_before + after.name + scope_after

    @staticmethod
    def clean_redundant_fields(container: TestResultContainer):
        # Do not save redundant data into json file
        container.glamor_setup_name = None
        container.glamor_setup_hidden = None
        container.glamor_teardown_name = None
        container.glamor_teardown_hidden = None
        container.glamor_scope = None
        container.glamor_autouse = None


allure.plugin_manager.register(GlamorReportLogger())
