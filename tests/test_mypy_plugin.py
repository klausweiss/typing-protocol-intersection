import typing
from pathlib import Path

import mypy.api
import pytest

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
        if line.strip().startswith("#") and "expected" in line:
            break
        stdout_lines.append(line.removeprefix("# "))
    return "\n".join(stdout_lines)


def get_expected_stderr(contents: str) -> str:
    lines = iter(contents.splitlines())
    stderr_lines = []
    for line in lines:
        if line.strip().startswith("#") and "expected stderr" in line:
            break
    for line in lines:
        if line.strip().startswith("#") and "expected" in line:
            break
        stderr_lines.append(line.removeprefix("# "))
    return "\n".join(stderr_lines)


@pytest.fixture()
def testcase_file(request):
    path = request.param
    with open(HERE / path) as f:
        contents = f.read()
    return _TestCase(HERE / path, get_expected_stdout(contents), get_expected_stderr(contents))


@pytest.mark.parametrize(
    "testcase_file",
    [
        pytest.param("testcases/in_generic_param_happy_path.py", id="generic param - happy path"),
        pytest.param(
            "testcases/in_generic_param_unhappy_path.py",
            id="generic param - unhappy path",
        ),
    ],
    indirect=["testcase_file"],
)
def test_mypy_plugin(testcase_file: _TestCase):
    stdout, stderr, _ = mypy.api.run([str(testcase_file.path), "--config-file", str(HERE / "test-mypy.ini")])
    assert (stdout.strip(), stderr.strip()) == (testcase_file.expected_stdout, testcase_file.expected_stderr)
