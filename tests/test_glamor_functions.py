"""
Here we test `glamor.include_scope_in_title` and
`glamor.logging_allure_steps` functions.
"""

import io
import logging

from allure_commons_test.container import has_container
from allure_commons_test.report import has_test_case
from hamcrest import assert_that

from glamor.patches import PatchHelper, include_scope_in_title
import glamor as allure
import pitest as pytest

from .matchers import has_after, has_before

autouse_values = ('True', 'False')
scopes = ('function', 'class', 'module', 'package', 'session')


def scopes_ids(val):
    return f'scope={val}'


def autouse_ids(val):
    return f'autouse={val}'


@pytest.mark.parametrize('autouse', autouse_values, ids=autouse_ids)
@pytest.mark.parametrize('scope', scopes, ids=scopes_ids)
@pytest.mark.parametrize('place', ('before', 'after'))
@pytest.mark.parametrize('include_autouse', autouse_values)
class TestInclude:
    @pytest.fixture
    def monkey_patchhelper(self):
        p = PatchHelper
        backup_add_autouse = getattr(p, '_add_autouse')
        backup_add_scope_after_name = getattr(p, '_add_scope_after_name')
        backup_add_scope_before_name = getattr(p, '_add_scope_before_name')
        yield
        setattr(p, '_add_autouse', backup_add_autouse)
        setattr(p, '_add_scope_after_name', backup_add_scope_after_name)
        setattr(p, '_add_scope_before_name', backup_add_scope_before_name)
        include_scope_in_title.called = False

    def test_scope_autouse(
        self,
        glamor_pytester,
        scope: str,
        autouse: str,
        place: str,
        include_autouse: str,
        monkey_patchhelper,
    ):
        setup = 'FANCY setup name'
        tear = 'FANCY teardown name'
        test_name = 'test_test'
        fixt_one = 'fixture_one'
        fixt_two = 'fixture_two'
        autouse_prefix = 'a' if {autouse, include_autouse} == {'True'} else ''

        glamor_pytester.pytester.makepyfile(f"""
            import glamor as allure
            import pitest as pytest

            allure.include_scope_in_title('{place}', autouse={include_autouse})

            @pytest.fixture(scope='{scope}', autouse={autouse})
            @allure.title.setup('{setup}')
            @allure.title.teardown('{tear}')
            def {fixt_one}():
                yield

            @pytest.fixture
            def {fixt_two}():
                yield

            def {test_name}({fixt_one}, {fixt_two}):
                pass

            """)
        prefix = f'[{scope[:1].upper()}{autouse_prefix}]'
        if place == 'before':
            prefixed_setup_one = f'{prefix} {setup}'
            prefixed_tear_one = f'{prefix} {tear}'
            prefixed_fixt_two = f'[F] {fixt_two}'
        elif place == 'after':
            prefixed_setup_one = f'{setup} {prefix}'
            prefixed_tear_one = f'{tear} {prefix}'
            prefixed_fixt_two = f'{fixt_two} [F]'
        else:
            raise RuntimeError('Unknown "place" parameter')

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    has_before(prefixed_setup_one),
                    has_after(prefixed_tear_one),
                ),
                has_container(
                    report,
                    has_before(prefixed_fixt_two),
                    has_after(prefixed_fixt_two),
                ),
            ),
        )

    def test_fixture_as_method(
        self,
        glamor_pytester,
        scope: str,
        autouse: str,
        place: str,
        include_autouse: str,
        monkey_patchhelper,
    ):
        fixt_name = 'fixt'
        test_name = 'test_in_class'

        glamor_pytester.pytester.makepyfile(f"""
            import pitest as pytest
            import glamor as allure

            allure.include_scope_in_title('{place}', autouse={include_autouse})

            class TestClass:
                @pytest.fixture(scope='{scope}', autouse={autouse})
                def {fixt_name}(self):
                    yield

                def {test_name}(self, fixt):
                    pass
            """)

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        autouse_prefix = 'a' if {autouse, include_autouse} == {'True'} else ''
        prefix = f'[{scope[:1].upper()}{autouse_prefix}]'
        if place == 'before':
            fixt_title = f'{prefix} {fixt_name}'
        elif place == 'after':
            fixt_title = f'{fixt_name} {prefix}'
        else:
            raise RuntimeError('Unknown "place" parameter')

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    has_before(fixt_title),
                    has_after(fixt_title),
                ),
            ),
        )


class TestLogging:
    logger_name = 'GlamorAsAllureLogger'

    @pytest.fixture(autouse=True)
    def backup_and_store_step_ctx(self):
        backup_enter = allure.step_ctx.__enter__
        yield
        allure.step_ctx.__enter__ = backup_enter

    @pytest.fixture
    def logger_stream(self):
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.INFO)
        stream = io.StringIO()
        handler = logging.StreamHandler(stream=stream)
        handler.setLevel(logging.INFO)
        fmt = logging.Formatter('[%(levelname)s] %(message)s')
        handler.setFormatter(fmt)
        logger.addHandler(handler)

        yield logger, stream

        logger.handlers.clear()

    @pytest.mark.parametrize('switch', ('on', 'off'))
    @pytest.mark.parametrize('times', (1, 2), ids=('once', 'twice'))
    def test_logging_step_can_be_on_or_off(self, logger_stream, switch, times):
        logger, stream = logger_stream
        for i in range(times):
            allure.logging_allure_steps(logger if switch == 'on' else None)

        expected_messages = []

        logger.info('start message')
        expected_messages.append('[INFO] start message')

        with allure.step('step message'):
            if switch == 'on':
                expected_messages.append('[STEP] step message')

        logger.error('end message')
        expected_messages.append('[ERROR] end message')

        logger_messages = stream.getvalue().strip().split('\n')
        assert logger_messages == expected_messages

    @pytest.mark.parametrize('start', ('on', 'off'))
    @pytest.mark.parametrize('steps', (1, 2, 3, 4))
    def test_logging_state_can_be_changed(self, start, logger_stream, steps):
        logger, stream = logger_stream

        expected_messages = []

        odd = logger if start == 'on' else None
        even = None if start == 'on' else logger

        allure.logging_allure_steps(odd)
        with allure.step('one'):
            if odd:
                expected_messages.append('[STEP] one')

        if steps >= 2:
            allure.logging_allure_steps(even)
            with allure.step('two'):
                if even:
                    expected_messages.append('[STEP] two')

        if steps >= 3:
            allure.logging_allure_steps(odd)
            with allure.step('three'):
                if odd:
                    expected_messages.append('[STEP] three')

        if steps >= 4:
            allure.logging_allure_steps(even)
            with allure.step('four'):
                if even:
                    expected_messages.append('[STEP] four')

        logger_messages_str = stream.getvalue().strip()
        if logger_messages_str:
            logger_messages = logger_messages_str.split('\n')
        else:
            logger_messages = []

        assert expected_messages == logger_messages
