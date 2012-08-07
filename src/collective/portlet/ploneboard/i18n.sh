#!/bin/sh

DOMAIN='collective.portlet.ploneboard'

if test -e locales/manual.pot; then
echo "Manual PO entries detected"
        MERGE="--merge locales/manual.pot"
else
echo "No manual PO entries detected"
        MERGE=""
fi


echo "Rebuild .pot file"
i18ndude rebuild-pot --pot locales/${DOMAIN}.pot ${MERGE} --create ${DOMAIN} --exclude="_backup" .

echo "Syncing .po files"
i18ndude sync --pot locales/${DOMAIN}.pot locales/*/LC_MESSAGES/${DOMAIN}.po

# Compile po files
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        msgfmt -o $lang/LC_MESSAGES/${DOMAIN}.mo $lang/LC_MESSAGES/${DOMAIN}.po
    fi
done


