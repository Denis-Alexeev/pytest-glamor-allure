"""Here we test that `glamor.tittle.setup` and `glamor.title.teardown`
decorators behave as expected."""

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
from .test_glamor_functions import (
    autouse_ids,
    autouse_values,
    scopes,
    scopes_ids,
)


@pytest.mark.parametrize('scope', scopes, ids=scopes_ids)
@pytest.mark.parametrize('autouse', autouse_values, ids=autouse_ids)
class TestOneFixtureOneTest:
    def test_setup_name_yield(self, glamor_pytester, scope, autouse):
        test_name = 'test_simple'
        fixt_name = 'simple_yield_fixture'
        setup_name = 'FANCY SETUP NAME'
        glamor_pytester.pytester.makepyfile(
            """
            import pitest as pytest
            import glamor as allure

            @pytest.fixture(scope='{scope}', autouse={autouse})
            @allure.title.setup('{setup_name}')
            def {fixt_name}():
                yield 777

            def {test_name}({fixt_name}):
                pass

            """.format(
                test_name=test_name,
                fixt_name=fixt_name,
                setup_name=setup_name,
                scope=scope,
                autouse=autouse,
            )
        )

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    has_before(setup_name),
                    not_(has_before(fixt_name)),
                    not_(has_glamor_befores()),
                    has_after(fixt_name),
                    not_(has_after(setup_name)),
                    not_(has_glamor_afters()),
                ),
            ),
        )

    def test_setup_name_return(self, glamor_pytester, scope, autouse):
        test_name = 'test_simple'
        fixt_name = 'simple_return_fixture'
        setup_name = 'FANCY SETUP NAME'
        glamor_pytester.pytester.makepyfile(
            """
            import pitest as pytest
            import glamor as allure

            @pytest.fixture(scope='{scope}', autouse={autouse})
            @allure.title.setup('{setup_name}')
            def {fixt_name}():
                return 777

            def {test_name}({fixt_name}):
                pass

            """.format(
                test_name=test_name,
                fixt_name=fixt_name,
                setup_name=setup_name,
                scope=scope,
                autouse=autouse,
            )
        )

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    has_before(setup_name),
                    not_(has_before(fixt_name)),
                    not_(has_glamor_befores()),
                    not_(has_after()),
                    not_(has_glamor_afters()),
                ),
            ),
        )

    def test_teardown_name_yield(self, glamor_pytester, scope, autouse):
        test_name = 'test_simple'
        fixt_name = 'simple_yield_fixture'
        teardown_name = 'FANCY TEARDOWN NAME'
        glamor_pytester.pytester.makepyfile(
            """
            import pitest as pytest
            import glamor as allure

            @pytest.fixture(scope='{scope}', autouse={autouse})
            @allure.title.teardown('{teardown_name}')
            def {fixt_name}():
                yield 777

            def {test_name}({fixt_name}):
                pass

            """.format(
                test_name=test_name,
                fixt_name=fixt_name,
                teardown_name=teardown_name,
                scope=scope,
                autouse=autouse,
            )
        )

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    has_before(fixt_name),
                    not_(has_before(teardown_name)),
                    not_(has_glamor_befores()),
                    has_after(teardown_name),
                    not_(has_after(fixt_name)),
                    not_(has_glamor_afters()),
                ),
            ),
        )

    def test_teardown_name_return(self, glamor_pytester, scope, autouse):
        test_name = 'test_simple'
        fixt_name = 'simple_return_fixture'
        teardown_name = 'FANCY TEARDOWN NAME'
        glamor_pytester.pytester.makepyfile(
            """
            import pitest as pytest
            import glamor as allure

            @pytest.fixture(scope='{scope}', autouse={autouse})
            @allure.title.teardown('{teardown_name}')
            def {fixt_name}():
                return 777

            def {test_name}({fixt_name}):
                pass

            """.format(
                test_name=test_name,
                fixt_name=fixt_name,
                teardown_name=teardown_name,
                scope=scope,
                autouse=autouse,
            )
        )

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    has_before(fixt_name),
                    not_(has_before(teardown_name)),
                    not_(has_glamor_befores()),
                    not_(has_after()),
                    not_(has_glamor_afters()),
                ),
            ),
        )

    with_name_ids = ('with_name', 'w/o_name')

    @pytest.mark.parametrize('with_name', (True, False), ids=with_name_ids)
    def test_setup_hidden_yield(
        self, glamor_pytester, scope, autouse, with_name
    ):
        test_name = 'test_simple'
        fixt_name = 'simple_yield_fixture'
        setup = 'bare fixture name is stored in json if "hidden=True"'
        glamor_pytester.pytester.makepyfile(
            """
            import pitest as pytest
            import glamor as allure

            @pytest.fixture(scope='{scope}', autouse={autouse})
            @allure.title.setup({setup_name}hidden=True)
            def {fixt_name}():
                yield 777

            def {test_name}({fixt_name}):
                pass

            """.format(
                test_name=test_name,
                fixt_name=fixt_name,
                scope=scope,
                autouse=autouse,
                setup_name=f"'{setup}', " if with_name else '',
            )
        )

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    has_glamor_befores(fixt_name),
                    not_(has_glamor_befores(setup)),
                    not_(has_before()),
                    has_after(fixt_name),
                    not_(has_after(setup)),
                    not_(has_glamor_afters()),
                ),
            ),
        )

    @pytest.mark.parametrize('with_name', (True, False), ids=with_name_ids)
    def test_setup_hidden_return(
        self, glamor_pytester, scope, autouse, with_name
    ):
        test_name = 'test_simple'
        fixt_name = 'simple_yield_fixture'
        setup = 'bare fixture name is stored in json if "hidden=True"'
        glamor_pytester.pytester.makepyfile(
            """
            import pitest as pytest
            import glamor as allure

            @pytest.fixture(scope='{scope}', autouse={autouse})
            @allure.title.setup({setup_name}hidden=True)
            def {fixt_name}():
                return 777

            def {test_name}({fixt_name}):
                pass

            """.format(
                test_name=test_name,
                fixt_name=fixt_name,
                scope=scope,
                autouse=autouse,
                setup_name=f"'{setup}', " if with_name else '',
            )
        )

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    has_glamor_befores(fixt_name),
                    not_(has_glamor_befores(setup)),
                    not_(has_before()),
                    not_(has_after()),
                    not_(has_glamor_afters()),
                ),
            ),
        )

    @pytest.mark.parametrize('with_name', (True, False), ids=with_name_ids)
    def test_teardown_hidden_yield(
        self, glamor_pytester, scope, autouse, with_name
    ):
        test_name = 'test_simple'
        fixt_name = 'simple_yield_fixture'
        tear = 'bare fixture name is stored in json if "hidden=True"'
        glamor_pytester.pytester.makepyfile(
            """
            import pitest as pytest
            import glamor as allure

            @pytest.fixture(scope='{scope}', autouse={autouse})
            @allure.title.teardown({tear}hidden=True)
            def {fixt_name}():
                yield 777

            def {test_name}({fixt_name}):
                pass

            """.format(
                test_name=test_name,
                fixt_name=fixt_name,
                scope=scope,
                autouse=autouse,
                tear=f"'{tear}', " if with_name else '',
            )
        )

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    not_(has_glamor_befores()),
                    not_(has_before(tear)),
                    has_before(fixt_name),
                    not_(has_after()),
                    not_(has_glamor_afters(tear)),
                    has_glamor_afters(f'{fixt_name}::0'),
                ),
            ),
        )

    @pytest.mark.parametrize('with_name', (True, False), ids=with_name_ids)
    def test_teardown_hidden_return(
        self, glamor_pytester, scope, autouse, with_name
    ):
        test_name = 'test_simple'
        fixt_name = 'simple_yield_fixture'
        tear = 'bare fixture name is stored in json if "hidden=True"'
        glamor_pytester.pytester.makepyfile(
            """
            import pitest as pytest
            import glamor as allure

            @pytest.fixture(scope='{scope}', autouse={autouse})
            @allure.title.teardown({tear}hidden=True)
            def {fixt_name}():
                return 777

            def {test_name}({fixt_name}):
                pass

            """.format(
                test_name=test_name,
                fixt_name=fixt_name,
                scope=scope,
                autouse=autouse,
                tear=f"'{tear}', " if with_name else '',
            )
        )

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    not_(has_glamor_befores()),
                    not_(has_before(tear)),
                    has_before(fixt_name),
                    not_(has_after()),
                    not_(has_glamor_afters()),
                ),
            ),
        )

    decor_orders = ('fst', 'fts', 'tfs', 'tsf', 'sft', 'stf')

    # 'fst' means order of decorators: fixture(), setup(), teardown()

    @pytest.mark.parametrize('order', decor_orders)
    def test_setup_and_tear_yield(
        self, glamor_pytester, scope, autouse, order
    ):
        test_name = 'test_simple'
        fixt_name = 'simple_yield_fixture'
        setup = 'fancy setup name'
        tear = 'fancy teardown name'
        setup_decor = f'@allure.title.setup("{setup}")'
        teardown_decor = f'@allure.title.teardown("{tear}")'
        fixture_decor = f'@pytest.fixture(scope="{scope}", autouse={autouse})'

        order_map = {'f': fixture_decor, 's': setup_decor, 't': teardown_decor}

        glamor_pytester.pytester.makepyfile(
            """
            import pitest as pytest
            import glamor as allure

            {decor_0}
            {decor_1}
            {decor_2}
            def {fixt_name}():
                yield 777

            def {test_name}({fixt_name}):
                pass
            """.format(
                test_name=test_name,
                fixt_name=fixt_name,
                decor_0=order_map[order[0]],
                decor_1=order_map[order[1]],
                decor_2=order_map[order[2]],
            )
        )

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    has_before(setup),
                    not_(has_before(tear)),
                    not_(has_before(fixt_name)),
                    not_(has_glamor_befores()),
                    has_after(tear),
                    not_(has_after(setup)),
                    not_(has_after(fixt_name)),
                    not_(has_glamor_afters()),
                ),
            ),
        )

    @pytest.mark.parametrize('order', decor_orders)
    def test_setup_and_tear_return(
        self, glamor_pytester, scope, autouse, order
    ):
        test_name = 'test_simple'
        fixt_name = 'simple_yield_fixture'
        setup = 'fancy setup name'
        tear = 'fancy teardown name'
        setup_decor = f'@allure.title.setup("{setup}")'
        teardown_decor = f'@allure.title.teardown("{tear}")'
        fixture_decor = f'@pytest.fixture(scope="{scope}", autouse={autouse})'

        order_map = {'f': fixture_decor, 's': setup_decor, 't': teardown_decor}

        glamor_pytester.pytester.makepyfile(
            """
            import pitest as pytest
            import glamor as allure

            {decor_0}
            {decor_1}
            {decor_2}
            def {fixt_name}():
                return 777

            def {test_name}({fixt_name}):
                pass

            """.format(
                test_name=test_name,
                fixt_name=fixt_name,
                decor_0=order_map[order[0]],
                decor_1=order_map[order[1]],
                decor_2=order_map[order[2]],
            )
        )

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_name,
                has_container(
                    report,
                    has_before(setup),
                    not_(has_before(tear)),
                    not_(has_before(fixt_name)),
                    not_(has_glamor_befores()),
                    not_(has_after()),
                    not_(has_glamor_afters()),
                ),
            ),
        )

    def test_fixture_as_method(self, glamor_pytester, scope, autouse):
        fixt_name = 'fixt'
        test_name = 'test_method'
        test_title = 'Test Title'
        setup = 'setup title'
        tear = 'teardown title'

        glamor_pytester.pytester.makepyfile(f"""
            import glamor as allure
            import pitest as pytest

            class TestClass:
                @pytest.fixture(scope='{scope}', autouse={autouse})
                @allure.title.setup('{setup}')
                @allure.title.teardown('{tear}')
                def {fixt_name}(self):
                    yield 777

                @allure.title('{test_title}')
                def {test_name}(self, {fixt_name}):
                    pass
            """)

        glamor_pytester.runpytest()
        report = glamor_pytester.allure_report

        assert_that(
            report,
            has_test_case(
                test_title,
                has_container(
                    report,
                    has_before(setup),
                    not_(has_before(tear)),
                    not_(has_before(fixt_name)),
                    not_(has_glamor_befores()),
                    has_after(tear),
                    not_(has_after(setup)),
                    not_(has_after(fixt_name)),
                    not_(has_glamor_afters()),
                ),
            ),
        )
