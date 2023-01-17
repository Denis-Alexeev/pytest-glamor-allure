from typing import TYPE_CHECKING, List, Tuple
import os
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

GLAMOR_TESTING_MODE = os.environ.get('GLAMOR_TESTING_MODE', False)


@attr.s
class TestResultContainer(TestResultContainer):
    """Recreate the class from allure lib.
    Allure uses "asdict" function from "attrs" lib to discover which
    attributes must be stored in json. "asdict" discovers only attributes which
    were in class during module initialization. We recreate class with
    additional attributes, and then: "container.__class__ = OurClass".

    """

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


@pytest.hookimpl(hookwrapper=True)
def pytest_sessionstart(session: pytest.Session):
    yield
    PatchHelper.fixt_mgr = getattr(session, '_fixturemanager', None)


@pytest.hookimpl(tryfirst=True)
def pytest_fixture_post_finalizer(
    fixturedef: pytest.FixtureDef,
    request: pytest.FixtureRequest,
):
    """Fetch info from fixture object and store in allure container.

    :param fixturedef: pytest.FixtureDef instance. According to hookspec.
    :param request: pytest.FixtureRequest. According to hookspec.
    """
    if PatchHelper.fixt_mgr is None:
        return

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
    if func is pytest.get_direct_param_fixture_func:
        return

    teardown_name = getattr(func, '__glamor_teardown_display_name__', None)
    teardown_hidden = getattr(
        func, '__glamor_teardown_display_hidden__', False
    )
    setup_name = getattr(func, '__glamor_setup_display_name__', None)
    setup_hidden = getattr(func, '__glamor_setup_display_hidden__', False)

    container.glamor_setup_name = setup_name
    container.glamor_setup_hidden = setup_hidden
    container.glamor_teardown_name = teardown_name
    container.glamor_teardown_hidden = teardown_hidden
    container.glamor_scope = fixturedef.scope
    container.glamor_autouse = PatchHelper.fixture_has_autouse(fixturedef)


class GlamorReportLogger:
    @allure.hookimpl(tryfirst=True, hookwrapper=True)
    def start_step(self, uuid, title, params):
        if PatchHelper.logger:
            PatchHelper.logger.log(PatchHelper.level, title)
        yield

    @allure.hookimpl(tryfirst=True, hookwrapper=True)
    def report_container(self, container: TestResultContainer):
        """Fetch stored in container data and handle.

        :param container: represents allure fixture json as python object
        """
        if not hasattr(container, 'glamor_setup_name'):
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
    def handle_scope(container: TestResultContainer) -> Tuple[str, str]:
        """Calculate letters representing "scope" and "autouse".
        They may be included before or after title. Both can be empty.
        One of them is always empty.

        :param container: represents allure fixture json as python object
        :return: letters before and after title. Example: ('[Sa] ', '')

        """
        autouse = ''
        if PatchHelper.i_should_add_autouse() and container.glamor_autouse:
            autouse = 'a'

        scope_before = ''
        scope_after = ''
        scope = f'[{container.glamor_scope[:1].upper()}{autouse}]'
        if PatchHelper.i_should_add_scope_before():
            scope_before = scope + ' '
        elif PatchHelper.i_should_add_scope_after():
            scope_after = ' ' + scope

        return scope_before, scope_after

    @staticmethod
    def handle_hidden_setup(container: TestResultContainer):
        """Clear "befores" list and save copy as "glamor_befores".

        :param container: represents allure fixture json as python object
        """
        befores_passed = {b.status for b in container.befores} == {'passed'}
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
        """Replace standard name with our fancy setup name.

        :param container: represents allure fixture json as python object
        :param scope_before: scope and autouse letters before title
        :param scope_after: scope and autouse letters after title
        """
        setup_name_is_str = isinstance(container.glamor_setup_name, str)
        for before in container.befores:
            if container.glamor_setup_name and setup_name_is_str:
                before.name = container.glamor_setup_name

            if isinstance(before.name, str):
                before.name = scope_before + before.name + scope_after

    @staticmethod
    def handle_hidden_teardown(container: TestResultContainer):
        """Clear "afters" list and save copy as "glamor_afters".

        :param container: represents allure fixture json as python object
        """
        afters_passed = {a.status for a in container.afters} == {'passed'}
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
        """Replace standard name with our fancy teardown name.

        :param container: represents allure fixture json as python object
        :type container: TestResultContainer
        :param scope_before: scope and autouse letters before title
        :param scope_after: scope and autouse letters after title
        """
        glamor_name = container.glamor_teardown_name
        tear_name_is_str = isinstance(container.glamor_teardown_name, str)
        for after in container.afters:
            if container.glamor_teardown_name and tear_name_is_str:
                new_name = re.sub('.*(?=::)', glamor_name, after.name, 1)
                after.name = new_name
            if len(container.afters) == 1 and isinstance(after.name, str):
                if after.name.endswith('::0'):
                    after.name = after.name[:-3]
            if isinstance(after.name, str):
                after.name = scope_before + after.name + scope_after

    @staticmethod
    def clean_redundant_fields(container: TestResultContainer):
        """Do not save redundant data into allure json container.
        Object is saved if (isinstance(obj, bool) or bool(obj) is True)

        :param container: represents allure fixture json as python object
        """
        container.glamor_setup_name = None
        container.glamor_setup_hidden = None
        container.glamor_teardown_name = None
        container.glamor_teardown_hidden = None
        container.glamor_scope = None
        container.glamor_autouse = None

        if not GLAMOR_TESTING_MODE:
            container.glamor_afters = None
            container.glamor_befores = None


allure.plugin_manager.register(GlamorReportLogger())
