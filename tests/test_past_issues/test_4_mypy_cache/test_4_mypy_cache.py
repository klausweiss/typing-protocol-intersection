"""
ref: https://github.com/klausweiss/typing-protocol-intersection/issues/4
"""

from pathlib import Path

HERE = Path(__file__).parent


def test_4_mypy_cache(run_mypy):
    # given
    input_file = HERE / "input.py"
    # when
    # This may not be 100% accurate, but when the bug was present, running mypy twice was (consistently) enough
    # to reproduce the issue. If there's no exception after 4 runs, we assume the bug's not there.
    for _ in range(4):
        run_mypy(input_file, no_incremental=False)
    # then no error
