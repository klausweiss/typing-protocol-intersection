# Running tests

Install [tox](https://pypi.org/project/tox/) and run:
```shell
tox
```

# Publishing a new release

1. Test with tox.
2. Update [`CHANGELOG.md`](./CHANGELOG.md).
3. Bump version in [`setup.cfg`](./setup.cfg).
4. Upload to pypi:
    ```shell
    python -m build
    twine check dist/*
    twine upload dist/* -r testpypi  # test before upload
    twine upload dist/*
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

