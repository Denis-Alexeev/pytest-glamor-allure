"""Here we test that `glamor.dynamic.title.setup` and
`glamor.dynamic.title.teardown` work as expected"""

from allure_commons_test.container import has_container
from allure_commons_test.report import has_test_case
from hamcrest import assert_that, not_

from .matchers import has_after, has_before


def test_fixture_as_func(glamor_pytester):
    glamor_pytester.makepyfile("""
        import pitest as pytest
        import glamor as allure

        @pytest.fixture
        def fixture():
            allure.dynamic.title.setup('Fancy setup')
            allure.dynamic.title.teardown('Fancy teardown')
            yield

        def test_test(fixture):
            pass
    """)

    glamor_pytester.runpytest()
    report = glamor_pytester.allure_report
    assert_that(
        report,
        has_test_case(
            'test_test',
            has_container(
                report,
                has_before('Fancy setup'),
                has_after('Fancy teardown'),
            ),
        ),
    )


def test_fixture_as_method(glamor_pytester):
    glamor_pytester.makepyfile("""
        import pitest as pytest
        import glamor as allure

        class TestClass:
            @pytest.fixture
            def fixture(self):
                allure.dynamic.title.setup('Setup name')
                yield
                allure.dynamic.title.teardown('Teardown name')

            def test_method(self, fixture):
                pass
        """)

    glamor_pytester.runpytest()
    report = glamor_pytester.allure_report
    assert_that(
        report,
        has_test_case(
            'test_method',
            has_container(
                report,
                has_before('Setup name'),
                has_after('Teardown name'),
            ),
        ),
    )


def test_override_fixture_in_class(glamor_pytester):
    glamor_pytester.makepyfile("""
        import glamor as allure
        import pitest as pytest

        @pytest.fixture
        @allure.title('Outer fixture')
        def fixture():
            yield

        class TestClass:
            @pytest.fixture
            def fixture(self):
                allure.dynamic.title.teardown('Inner fixture teardown')
                yield
                allure.dynamic.title.setup('Inner fixture setup')

            def test_inner(self, fixture):
                pass
        """)

    glamor_pytester.runpytest()
    report = glamor_pytester.allure_report
    assert_that(
        report,
        has_test_case(
            'test_inner',
            has_container(
                report,
                has_after('Inner fixture teardown'),
                has_before('Inner fixture setup'),
                not_(has_after('before')),
                not_(has_before('fixture')),
            ),
        ),
    )


def test_override_conftest_fixture(glamor_pytester):
    glamor_pytester.makeconftest("""
        import pytest
        import glamor as allure

        @pytest.fixture
        def fixture():
            allure.dynamic.title.setup('Conftest setup')
            allure.dynamic.title.teardown('Conftest teardown')
            yield
        """)
    glamor_pytester.makepyfile("""
        import pytest
        import glamor as allure

        @pytest.fixture
        def fixture():
            allure.dynamic.title.setup('module setup name')
            allure.dynamic.title.teardown('module teardown name')
            yield

        def test_module(fixture):
            pass
        """)

    glamor_pytester.runpytest()
    report = glamor_pytester.allure_report
    assert_that(
        report,
        has_test_case(
            'test_module',
            has_container(
                report,
                has_before('module setup name'),
                not_(has_before('Conftest setup')),
                has_after('module teardown name'),
                not_(has_after('Conftest teardown')),
            ),
        ),
    )
