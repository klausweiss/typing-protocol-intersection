import typing
from pathlib import Path

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
def testcase_file(request, strip_invisible):
    path = request.param
    with open(HERE / path, encoding="utf-8") as file:
        contents = file.read()
    return _TestCase(
        HERE / path,
        strip_invisible(get_expected_stdout(contents)),
        strip_invisible(get_expected_stderr(contents)),
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
def test_mypy_plugin(testcase_file: _TestCase, run_mypy):
    stdout, stderr = run_mypy(testcase_file.path)
    assert (stdout.strip(), stderr.strip()) == (testcase_file.expected_stdout, testcase_file.expected_stderr)


@pytest.mark.parametrize(
    "version",
    [
        pytest.param("0.910", id="0.910 - before the first supported 0.920"),
        pytest.param("0.992", id="0.992 - non-existent version greater than the last tested 0.x"),
        pytest.param("1.15.0", id="1.15.0 - first greater than 1.14.x with breaking changes"),
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
        pytest.param("1.1.1", id="1.1.1 - some 1.1.x version"),
        pytest.param("1.2.0", id="1.2.0 - some 1.2.x version"),
        pytest.param("1.3.0", id="1.3.0 - some 1.3.x version"),
        pytest.param("1.4.0", id="1.4.0 - some 1.4.x version"),
        pytest.param("1.5.0", id="1.5.0 - some 1.5.x version"),
        pytest.param("1.6.0", id="1.6.0 - some 1.6.x version"),
        pytest.param("1.7.0", id="1.7.0 - some 1.7.x version"),
        pytest.param("1.8.0", id="1.8.0 - some 1.8.x version"),
        pytest.param("1.9.0", id="1.9.0 - some 1.9.x version"),
        pytest.param("1.10.0", id="1.10.0 - some 1.10.x version"),
        pytest.param("1.11.0", id="1.11.0 - some 1.11.x version"),
        pytest.param("1.11.0", id="1.11.0 - some 1.11.x version"),
        pytest.param("1.12.0", id="1.12.0 - some 1.12.x version"),
        pytest.param("1.13.0", id="1.13.0 - some 1.13.x version"),
        pytest.param("1.14.0", id="1.14.0 - some 1.14.x version"),
    ],
)
def test_initializes_for_supported_mypy_versions(version: str) -> None:
    # when
    _plugin = typing_protocol_intersection.mypy_plugin.plugin(version)
    # then no exception
