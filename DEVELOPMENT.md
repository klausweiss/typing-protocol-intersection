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
