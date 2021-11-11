from typing import Optional

from allure_commons_test.report import AllureReport

import pitest as pytest

pytest_plugins = "pytester"


class GlamorPytester:
    def __init__(self, pytester: pytest.Pytester):
        self.pytester = pytester
        self.allure_report: Optional[AllureReport] = None

    def runpytest(self, *args, **kwargs):
        self.pytester.runpytest(
            "--alluredir", str(self.pytester.path), *args, **kwargs
        )
        self.allure_report = AllureReport(str(self.pytester.path))


@pytest.fixture
def glamor_pytester(pytester: pytest.Pytester):
    return GlamorPytester(pytester)
