import sys

from pytest import *
from _pytest import outcomes, skipping
from _pytest.config import (
    Config,
    PluginManager,
    PytestPluginManager,
    create_terminal_writer,
)
from _pytest.fixtures import (
    FixtureDef,
    FixtureManager,
    FixtureRequest,
    SubRequest,
    getfixturemarker,
)
from _pytest.junitxml import LogXML
from _pytest.mark import Mark
from _pytest.nodes import Item, Node
from _pytest.outcomes import (
    Exit,
    Failed,
    Skipped,
    XFailed,
)
from _pytest.pytester import Pytester
from _pytest.python import Function

try:
    from _pytest.outcomes import (
        _with_exception as with_exception,
    )  # pytest v9 cut out
    from _pytest.python import Metafunc  # pytest v9 cut out
except ImportError:

    def with_exception(func):
        """
        Replacing the old _with_exception that was removed from pytest v9
        """
        try:
            return func()
        except skip.Exception as e:
            raise
        except AssertionError:
            raise
        except BaseException as e:
            tb = sys.exc_info()[2]
            raise e.with_traceback(tb)


from _pytest.reports import CollectReport, TestReport

try:
    from _pytest.fixtures import get_direct_param_fixture_func

    # pytest versions up to 7.*.*
except ImportError:
    from _pytest.python import get_direct_param_fixture_func

    # pytest versions from 8.*.*
