"""Here we test that we do not break allure or pytest behaviour.
Our goal is to supplement them but not to change it (or even break)."""

from allure_commons_test.container import has_container
from allure_commons_test.report import has_test_case
from hamcrest import assert_that, not_

import pitest as pytest

from .matchers import (
    has_after,
    has_before,
    has_glamor_afters,
    has_glamor_befores,
)


def test_parametrized(glamor_pytester):
    glamor_pytester.pytester.makepyfile("""
        import glamor as allure
        import pytest

        @pytest.fixture
        @allure.title.setup('setup')
        @allure.title.teardown('tear')
        def fixt():
            yield

        @pytest.mark.parametrize('param_func', ('a', 'b'))
        def test_func(param_func, fixt):
            pass


        @pytest.mark.parametrize('param_cls', ('c', 'd'))
        class TestClass:
            @pytest.mark.parametrize('param_meth', ('e', 'f'))
            def test_method(self, param_cls, param_meth, fixt):
                pass
        """)

    result = glamor_pytester.runpytest()
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=6)

    report = glamor_pytester.allure_report
    for func_param in ('a', 'b'):
        assert_that(
            report,
            has_test_case(
                f'test_func[{func_param}]',
                has_container(
                    report,
                    has_before('setup'),
                    not_(has_before('tear')),
                    not_(has_before('fixt')),
                    not_(has_before('param_func')),
                    not_(has_glamor_befores()),
                    has_after('tear'),
                    not_(has_after('setup')),
                    not_(has_after('fixt')),
                    not_(has_after('param_func')),
                    not_(has_glamor_afters()),
                ),
            ),
        )

    for meth_param in ('e', 'f'):
        for cls_param in ('c', 'd'):
            assert_that(
                report,
                has_test_case(
                    f'test_method[{meth_param}-{cls_param}]',
                    has_container(
                        report,
                        has_before('setup'),
                    ),
                ),
            )
