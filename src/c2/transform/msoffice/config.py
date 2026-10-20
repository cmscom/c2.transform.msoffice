import mimetypes


PROJECTNAME = "c2.transform.msoffice"
SITE_CHARSET = "utf-8"
TRANSFORM_NAME = "msoffice_to_text"

office_mimetypes = (
    {
        "name": "Office Word 2007 XML macro enabled document",
        "mimetypes": ("application/vnd.ms-word.document.macroEnabled.12",),
        "extensions": ("docm",),
    },
    {
        "name": "Office Word 2007 XML document",
        "mimetypes": (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        "extensions": ("docx",),
    },
    {
        "name": "Office Powerpoint 2007 macro-enabled XML presentation",
        "mimetypes": ("application/vnd.ms-powerpoint.presentation.macroEnabled.12",),
        "extensions": ("pptm",),
    },
    {
        "name": "Office Powerpoint 2007 XML presentation",
        "mimetypes": (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ),
        "extensions": ("pptx",),
    },
    {
        "name": "Office Excel 2007 binary workbook (BIFF12)",
        "mimetypes": ("application/vnd.ms-excel.sheet.binary.macroEnabled.12",),
        "extensions": ("xlsb",),
    },
    {
        "name": "Office Excel 2007 XML macro-enabled workbook",
        "mimetypes": ("application/vnd.ms-excel.sheet.macroEnabled.12",),
        "extensions": ("xlsm",),
    },
    {
        "name": "Office Excel 2007 XML workbook",
        "mimetypes": (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        "extensions": ("xlsx",),
    },
)

for mt in office_mimetypes:
    mt["globs"] = tuple("*." + ext for ext in mt["extensions"])
    mt["icon_path"] = "application.png"
    # plone.namedfile guesses a missing content type with the standard library.
    # Python < 3.14 does not know these types and slim images have no
    # /etc/mime.types, so they are added on import, in every process.
    mimetypes.add_type(mt["mimetypes"][0], "." + mt["extensions"][0])

del mimetypes
