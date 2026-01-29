from __future__ import annotations

from typing import TYPE_CHECKING, Union

from allure_commons_test.container import (
    has_after as allure_has_after,
    has_before as allure_has_before,
    has_fixture as has_section,
)
from hamcrest import has_key
from hamcrest.core.matcher import Matcher

if TYPE_CHECKING:
    from typing import Literal

afters: Union[str, 'Literal["afters"]'] = 'afters'
befores: Union[str, 'Literal["befores"]'] = 'befores'
matchers_with_none = RuntimeError('matchers can not be used if name is None')
glamor = 'glamor'


def just_has_glamor(name: 'Literal["befores", "afters"]'):
    return has_key(f'{glamor}_{name}')


def has_glamor_befores(name: str = None, *matchers: Matcher):
    if name is None:
        if matchers:
            raise matchers_with_none
        return just_has_glamor(befores)
    return has_section(f'{glamor}_{befores}', name, *matchers)


def has_glamor_afters(name: str = None, *matchers: Matcher):
    if name is None:
        if matchers:
            raise matchers_with_none
        return just_has_glamor(afters)
    return has_section(f'{glamor}_{afters}', name, *matchers)


def has_before(name: str = None, *matchers: Matcher):
    if name is None:
        if matchers:
            raise matchers_with_none
        return has_key(befores)
    return allure_has_before(name, *matchers)


def has_after(name: str = None, *matchers: Matcher):
    if name is None:
        if matchers:
            raise matchers_with_none
        return has_key(afters)
    return allure_has_after(name, *matchers)
