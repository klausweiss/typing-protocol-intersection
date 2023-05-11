#!/usr/bin/env bash

SCRIPT_NAME=$0
NEW_VERSION=${1?Version argument is required}
NEW_MAJOR=`echo $NEW_VERSION | cut -d. -f1`
NEW_MINOR=`echo $NEW_VERSION | cut -d. -f2`
NEW_PATCH=`echo $NEW_VERSION | cut -d. -f3`
NEXT_MINOR=`echo $NEW_MINOR+1 | bc`

# change mypy plugin code
sed -E "s/(.*len\(parted_version\) == 3.*\()[0-9]+. [0-9]+, [0-9]+(\).*)/\1$NEW_MAJOR, $NEXT_MINOR, 0\2/" typing_protocol_intersection/mypy_plugin.py --in-place

# update tests

## test_initializes_for_supported_mypy_versions
NEW_TEST_LINE="        pytest.param(\"$NEW_MAJOR.$NEW_MINOR.$NEW_PATCH\", id=\"$NEW_MAJOR.$NEW_MINOR.$NEW_PATCH - some $NEW_MAJOR.$NEW_MINOR.x version\"),"
# the code below inserts the testcase defined above as the last item in the list of parameters to the test_initializes_for_supported_mypy_versions test
tmp=`mktemp`
awk -v n=2 -v pattern="test_initializes_for_supported_mypy_versions" -v insert_line="$NEW_TEST_LINE" '{
    lines[NR] = $0
    if (NR > n && $0 ~ pattern) {
        print insert_line
        for (i = NR - n; i < NR - 1; i++) {
            print lines[i]
        }
    } else {
        if (NR > n) print lines[NR - n]
    }
}
END {
    for (i = NR - n + 1; i <= NR; i++) {
        print lines[i]
    }
}' tests/test_mypy_plugin.py > $tmp
mv $tmp tests/test_mypy_plugin.py
## test_raises_for_unsupported_mypy_versions
NEW_TEST_LINE="        pytest.param(\"$NEW_MAJOR.$NEXT_MINOR.0\", id=\"$NEW_MAJOR.$NEXT_MINOR.0 - first greater than $NEW_MAJOR.$NEW_MINOR.x with breaking changes\"),"
sed -E      's/        pytest.param\(".*", id=".* - first greater than .* with breaking changes"\),/'"$NEW_TEST_LINE"'/' -i tests/test_mypy_plugin.py

# update readme
sed -E "s/(and mypy .* <= )\S+\.\S+\.\S+?(\..*)/\1$NEW_MAJOR.$NEW_MINOR.x\2/" README.md --in-place

# bump version in setup.cfg
PACKAGE_VERSION=`grep -E "version = .*" setup.cfg | sed "s/version = //"`
MAJOR_PACKAGE_VERSION=`echo $PACKAGE_VERSION | cut -d. -f1`
MINOR_PACKAGE_VERSION=`echo $PACKAGE_VERSION | cut -d. -f2`
PATCH_PACKAGE_VERSION=`echo $PACKAGE_VERSION | cut -d. -f3`
# patch until the first 1.0 release, then we can change to minor
NEW_PATCH_PACKAGE_VERSION=`echo $PATCH_PACKAGE_VERSION+1 | bc`
NEW_PACKAGE_VERSION="$MAJOR_PACKAGE_VERSION.$MINOR_PACKAGE_VERSION.$NEW_PATCH_PACKAGE_VERSION"
sed -E "s/(version = ).*/\1$NEW_PACKAGE_VERSION/" setup.cfg --in-place

# update changelog
RELEASE_NOTES=`cat <<EOF
Add support for mypy==$NEW_MAJOR.$NEW_MINOR.x.
EOF`
CHANGELOG_ENTRY=`cat <<EOF

## $NEW_PACKAGE_VERSION

$RELEASE_NOTES
EOF`

# the code below inserts text after the first occurrence of pattern
tmp=`mktemp`
awk \
	-v pattern="Changelog" \
	-v text="$CHANGELOG_ENTRY" '\
	{
    print
    if (!found && $0 ~ pattern) {
        found = 1
        print text
    } 
	}
	' CHANGELOG.md > $tmp
mv $tmp CHANGELOG.md


# autoformat
black .

# git add and commit
git add \
    typing_protocol_intersection/mypy_plugin.py \
    tests/test_mypy_plugin.py \
    README.md \
    setup.cfg \
    CHANGELOG.md
git commit -m "Add support for mypy==$NEW_MAJOR.$NEW_MINOR.x

This commit was generated with $SCRIPT_NAME"

# github release command

echo "gh release create '$NEW_PACKAGE_VERSION' --notes '$RELEASE_NOTES'"
