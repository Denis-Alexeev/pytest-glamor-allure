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
from _pytest.outcomes import Exit, Failed, Skipped, XFailed
from _pytest.pytester import Pytester
from _pytest.python import Function, Metafunc
from _pytest.reports import CollectReport, TestReport
import pytest

try:
    from _pytest.fixtures import get_direct_param_fixture_func

    # pytest versions up to 7.*.*
except ImportError:
    from _pytest.python import get_direct_param_fixture_func

    # pytest versions from 8.*.*


if (
    tuple(map(int, pytest.__version__.split('.')[:2]))[0] < 9
):  # pytest versions up to 9.*.*
    from _pytest.outcomes import _with_exception as with_exception
