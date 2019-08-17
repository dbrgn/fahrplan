# Release process

Signing key: https://keybase.io/dbrgn (F2F3A5FA)

Used variables:

    export VERSION={VERSION}
    export GPG=F2F3A5FA

Update version number in setup.py and CHANGELOG.md:

    vim -p fahrplan/meta.py CHANGELOG.md

Do a signed commit and signed tag of the release:

    git add fahrplan/meta.py CHANGELOG.md
    git commit -S${GPG} -m "Release v${VERSION}"
    git tag -u ${GPG} -m "Release v${VERSION}" v${VERSION}

Build source and binary distributions:

    python3 setup.py sdist
    python3 setup.py bdist_wheel

Sign files:

    gpg --detach-sign -u ${GPG} -a dist/fahrplan-${VERSION}.tar.gz
    gpg --detach-sign -u ${GPG} -a dist/fahrplan-${VERSION}-py3-none-any.whl

Upload package to PyPI:

    twine3 upload dist/fahrplan-${VERSION}*
    git push
    git push --tags
