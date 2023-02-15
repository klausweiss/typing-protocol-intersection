import typing
from pathlib import Path

import mypy.api
import mypy.version
import pytest

import typing_protocol_intersection.mypy_plugin

HERE = Path(__file__).parent


class _TestCase(typing.NamedTuple):
    path: Path
    expected_stdout: str
    expected_stderr: str


def get_expected_stdout(contents: str) -> str:
    lines = iter(contents.splitlines())
    stdout_lines = []
    for line in lines:
        if line.strip().startswith("#") and "expected stdout" in line:
            break
    for line in lines:
        if line.strip().startswith("#") and "expected stderr" in line:
            break
        if line.startswith("# "):
            stdout_lines.append(line[2:])
    return "\n".join(stdout_lines)


def get_expected_stderr(contents: str) -> str:
    lines = iter(contents.splitlines())
    stderr_lines = []
    for line in lines:
        if line.strip().startswith("#") and "expected stderr" in line:
            break
    for line in lines:
        if line.strip().startswith("#") and "expected stdout" in line:
            break
        if line.startswith("# "):
            stderr_lines.append(line[2:])
    return "\n".join(stderr_lines)


@pytest.fixture()
def testcase_file(request):
    path = request.param
    with open(HERE / path, encoding="utf-8") as file:
        contents = file.read()
    return _TestCase(
        HERE / path,
        _strip(get_expected_stdout(contents)),
        _strip(get_expected_stderr(contents)),
    )


@pytest.mark.parametrize(
    "testcase_file",
    [
        # region happy paths
        pytest.param("testcases/in_generic_param_happy_path.py", id="generic param - happy path"),
        pytest.param("testcases/in_generic_param_happy_path_covariant.py", id="generic param, covariant - happy path"),
        pytest.param("testcases/function_return_type_happy_path.py", id="function return type - happy path"),
        pytest.param("testcases/multiple_params_happy_path.py", id="accepts multiple type parameters - happy path"),
        pytest.param(
            "testcases/protocol_extending_another_property_happy_path.py",
            id="protocol extending another protocol that has a property - happy path",
        ),
        pytest.param(
            "testcases/protocol_extending_another_method_happy_path.py",
            id="protocol extending another protocol that has a method - happy path",
        ),
        pytest.param(
            "testcases/protocol_extending_another_builder_happy_path.py",
            id="protocol extending another protocol, passed as a generic param - happy path",
        ),
        # endregion
        # region unhappy paths
        pytest.param(
            "testcases/in_generic_param_unhappy_path.py",
            id="generic param - unhappy path",
        ),
        pytest.param(
            "testcases/fails_for_non_protocols.py",
            id="fails when defining a function/method whose return has a non-Protocol base class",
        ),
        pytest.param("testcases/function_return_type_unhappy_path.py", id="function return type - unhappy path"),
        pytest.param("testcases/multiple_params_unhappy_path.py", id="accepts multiple type parameters - unhappy path"),
        pytest.param(
            "testcases/protocol_extending_another_builder_unhappy_path.py",
            id="protocol extending another protocol, passed as a generic param - unhappy path",
        ),
        # endregion
    ],
    indirect=["testcase_file"],
)
def test_mypy_plugin(testcase_file: _TestCase):
    stdout, stderr = _run_mypy(testcase_file.path)
    assert (stdout.strip(), stderr.strip()) == (testcase_file.expected_stdout, testcase_file.expected_stderr)


def _run_mypy(input_file: Path) -> typing.Tuple[str, str]:
    stdout, stderr, _ = mypy.api.run(
        [str(input_file), "--config-file", str(HERE / "test-mypy.ini"), "--no-incremental"]
    )
    return _strip(stdout), _strip(stderr)


def _strip(string: str) -> str:
    """Removes all zero-width spaces from the input text and strips
    whitespaces.

    The need for the former was born with an ugly hack that we use to
    trick mypyc.
    """
    zero_width_space = "\u200B"
    return string.strip().replace(zero_width_space, "")


@pytest.mark.parametrize(
    "version",
    [
        pytest.param("0.910", id="0.910 - before the first supported 0.920"),
        pytest.param("0.992", id="0.992 - non-existent version greater than the last tested 0.x"),
        pytest.param("1.1.0", id="1.1.0 - first greater than 1.0.x with breaking changes"),
    ],
)
def test_raises_for_unsupported_mypy_versions(version: str) -> None:
    with pytest.raises(NotImplementedError):
        typing_protocol_intersection.mypy_plugin.plugin(version)


@pytest.mark.parametrize(
    "version",
    [
        pytest.param("0.920", id="0.920 - the first supported version"),
        pytest.param("0.991", id="0.991 - the last known 0.x version"),
        pytest.param("1.0.0", id="1.0.0 - the first 1.0.x version"),
        pytest.param("1.0.100", id="1.0.100 - some other 1.0.x version"),
    ],
)
def test_initializes_for_supported_mypy_versions(version: str) -> None:
    # when
    _plugin = typing_protocol_intersection.mypy_plugin.plugin(version)
    # then no exception
