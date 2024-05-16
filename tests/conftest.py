import typing
import re
from pathlib import Path

import mypy.api
import pytest

HERE = Path(__file__).parent


@pytest.fixture
def run_mypy(strip_invisible: typing.Callable[[str], str]):
    def _run_mypy(input_file: Path, no_incremental: bool = True) -> typing.Tuple[str, str]:
        args = [str(input_file), "--config-file", str(HERE / "test-mypy.ini")]
        if no_incremental:
            args.append("--no-incremental")
        stdout, stderr, _ = mypy.api.run(args)
        return fix_paths(strip_invisible(stdout)), fix_paths(strip_invisible(stderr))

    return _run_mypy


@pytest.fixture
def strip_invisible() -> typing.Callable[[str], str]:
    def _strip_invisible(string: str) -> str:
        """Removes all zero-width spaces from the input text and strips
        whitespaces.

        The need for the former was born with an ugly hack that we use
        to trick mypyc.
        """
        zero_width_space = "\u200B"
        return string.strip().replace(zero_width_space, "")

    return _strip_invisible


WindowsPyPathPattern = re.compile(r"[a-z_\\]+\.py")


def fix_paths(text: str) -> str:
    """On Windows the path separator is \\, not /. This makes all python paths in mypy output use / for consistency."""
    return WindowsPyPathPattern.sub(lambda l: l.group().replace("\\", "/"), text)
