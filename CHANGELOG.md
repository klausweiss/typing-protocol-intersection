# Changelog

## 0.6.0

- Drop support for Python 3.9.
- Drop support for mypy<1.5.0.
- Add support for mypy==1.18.x.
- Add support for Python 3.14.
- Use uv and ruff for dev environment, CI and linting.
- Mark package with free-threaded-support.

## 0.5.3

Add support for mypy==1.15.x.

## 0.5.2

Add support for mypy==1.14.x.

## 0.5.1

Add support for mypy==1.13.x.

## 0.5.0

- Drop support for Python 3.8.
- Add Python 3.13 support.
- Add support for mypy==1.12.x.

## 0.4.2

Add support for mypy==1.11.x.

## 0.4.1

Add support for mypy==1.10.x.

## 0.4.0

- Drop support for Python 3.7.
- Add support for mypy==1.9.x.

## 0.3.10

Add support for mypy==1.8.x.

## 0.3.9

Add support for mypy==1.7.x.

## 0.3.8

- Add support for mypy==1.6.x.
- Add Python 3.12 support.

## 0.3.7

Fixed mypy crashing in incremental mode (#5). Contributed by @drvink.

## 0.3.6

Add support for mypy==1.5.x.

## 0.3.5

Add support for mypy==1.5.x.

## 0.3.4

Add support for mypy==1.4.x.

## 0.3.3

Add support for mypy==1.3.x.

## 0.3.2

Add support for mypy==1.2.x.

## 0.3.1

Add support for mypy==1.1.x.

## 0.3.0

Add support for mypy==1.0.0.

## 0.2.3

Explicitly specify supported mypy versions as 0.920 <= x <= 0.991 and fail loudly for others.

## 0.2.2

Add Python 3.11 support.

## 0.2.1

Fix support for protocols inheriting another protocols when used as type arguments.

## 0.2

Fix support for protocols inheriting another protocols.

## 0.1.1

Add `py.typed` to the build artifact.

## 0.1

Initial version. Consists of a mypy plugin and a `ProtocolIntersection` type.
