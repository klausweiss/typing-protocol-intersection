# Running tests

Install [uv](https://docs.astral.sh/uv/) and run tests using the Makefile:
```shell
make install  # Install package and dependencies
make lint     # Run all linters (mypy, ruff check, ruff format --check, pylint)
make test     # Run tests with coverage
make format   # Format code with ruff
make all      # Run both lint and test
```

Alternatively, you can use [tox](https://pypi.org/project/tox/):
```shell
uv tool run tox
```

# Publishing a new release

1. Run tests as described above.
2. Update [`CHANGELOG.md`](./CHANGELOG.md).
3. Bump version in [`pyproject.toml`](./pyproject.toml).
4. Build and upload to pypi:
    ```shell
    uv build
    uv run twine check dist/*
    uv run twine upload dist/* -r testpypi  # test before upload
    uv run twine upload dist/*
    ```
5. Create a new release on [github](https://github.com/klausweiss/typing-protocol-intersection/releases).

# When a new mypy version is released

Mypy may introduce breaking changes in minor versions (see [this blogpost](https://mypy-lang.blogspot.com/2023/02/mypy-10-released.html)).
We don't want to risk false positives when stating the plugin works with mypy versions that haven't been tested and may have introduced breaking changes.
That's why for every minor mypy release, this plugin should be updated as well.
This can be a very repetitive process, so it has been automated.

When a new mypy version is released, run the following script:
```shell
./tools/prepare-pr-after-mypy-bump.sh NEW_MYPY_VERSIONS
```

It will make necessary changes to code and commit them.
Review the commit made by the plugin, run tests, and if it looks good, push.

