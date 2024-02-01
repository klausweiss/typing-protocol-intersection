"""
ref: https://github.com/klausweiss/typing-protocol-intersection/issues/8
"""

from pathlib import Path

HERE = Path(__file__).parent


def test_8_non_protocol_member(run_mypy):
    # given
    input_file = HERE / "input.py"
    # when
    stdout, _stderr = run_mypy(input_file, no_incremental=False)
    # then no error
    assert not stdout.startswith("Success")
    assert "error:" in stdout
    assert "Only Protocols can be used in ProtocolIntersection" in stdout
