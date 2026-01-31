import sys

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
from _pytest.outcomes import Exit, Failed, Skipped, XFailed
from _pytest.pytester import Pytester
from _pytest.python import Function, Metafunc
from _pytest.reports import CollectReport, TestReport
from pytest import *  # noqa: PT013
from pytest import version_tuple as pytest_version_tuple  # noqa: PT013

if int(pytest_version_tuple[0]) < 8:  # noqa: PLR2004 Magic value used in comparison
    from _pytest.fixtures import get_direct_param_fixture_func
    # pytest versions up to 7.*.*
else:
    from _pytest.python import get_direct_param_fixture_func
    # pytest versions from 8.*.*

if int(pytest_version_tuple[0]) < 9:  # noqa: PLR2004 Magic value used in comparison
    from _pytest.outcomes import _with_exception as with_exception
    # this function was deleted from pytest in version 9
