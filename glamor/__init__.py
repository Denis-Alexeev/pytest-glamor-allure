from allure import (
    attach,
    attachment_type,
    description,
    description_html,
    epic,
    feature,
    id,
    issue,
    label,
    link,
    parent_suite,
    severity,
    severity_level,
    step,
    story,
    sub_suite,
    suite,
    tag,
    testcase,
)
from allure_commons import hookimpl, plugin_manager
from allure_commons._allure import StepContext as step_ctx
from allure_commons.model2 import (
    Attachment,
    ExecutableItem,
    Label,
    Link,
    Parameter,
    Status,
    StatusDetails,
    TestAfterResult,
    TestBeforeResult,
    TestResult,
    TestResultContainer,
    TestStepResult,
)
from allure_commons.types import LabelType as label_type, LinkType as link_type
from allure_commons.utils import func_parameters, md5, now, platform_label
from allure_pytest.utils import (
    allure_description as get_description,
    allure_description_html as get_description_html,
    allure_full_name as get_full_name,
    allure_label as get_label,
    allure_labels as get_labels,
    allure_links as get_links,
    allure_name as get_name,
    allure_package as get_package,
    allure_suite_labels as get_suite_labels,
    allure_title as get_title,
    get_marker_value,
    get_outcome_status,
    get_outcome_status_details,
    get_pytest_report_status,
    get_status,
    get_status_details,
    pytest_markers,
)

try:
    from allure_pytest.utils import mark_to_str  # allure-pytest <= 2.14.3
except ImportError:
    pass

from .patches import (
    Dynamic as dynamic,
    include_scope_in_title,
    listener,
    logging_allure_steps,
    pytest_config,
    reporter,
    title,
)

del listener
del reporter
del pytest_config


def __getattr__(name):
    msg = f'{__name__} module does not contain "{name}" attribute'

    def get_listener():
        for plugin in plugin_manager._name2plugin.values():
            if plugin.__class__.__name__ == 'AllureListener':
                return plugin
        return None

    name_to_attr = {'reporter': 'allure_logger', 'pytest_config': 'config'}

    if name == 'listener':
        return get_listener()

    elif name in ('reporter', 'pytest_config'):
        return getattr(get_listener(), name_to_attr[name], None)

    raise AttributeError(msg)
