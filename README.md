Select LimbusCompany_Data folder to begin

Possible improvements:
	Better capitalization logic after all replacements (Word order change may result in wrong capitalization)
	Better logic for sentence full-stops (accounting for lower-case symbols)
	More abstract algorithm for <style> ignoring (now needs separate replace expression)


Configuration:

moveFiles

    enabled
        This parameter turns the copying of translation files on or off.

    sourceTranslation
        Specifies the folder name of the base translation, for example, "en".

    translationName
        Defines the folder name for the new translation

    moveFont
        Determines whether the font folder from project (Calibri) should be copied as well.
        This may be necessary for the translation to display correctly.

replaceFilesEnabled

    Enables or disables the replacement of strings in files according to the patterns specified in the "replace" section.
    When true, all specified replacements will be performed.

statuses

    enabled
        Activates the collection and replacement of status objects within files.

    replaceIcon
        Sets the string or symbol that will replace statuses.
        Can be an empty string if no replacement is desired.

    fields

        required
            Lists the mandatory fields an object must have to be considered a status.

        optional
            Lists additional fields that are allowed but not required for a status object.

    ignoredFiles
        Specifies files whose contents will not be checked for statuses.

skillTagPersistency

    Determines whether the first word in square brackets (e.g., [On kill]) is treated as a skill tag.
    If true, such tags will not be affected by replacement patterns below.

replace

    An array of objects specifying how and where to replace certain strings in translation files.

    Each object contains:

        fields
            An array of field names in which replacements should occur.

        changes
            An array of replacement rules, each with:

                from
                    The string or regular expression pattern to search for.

                to
                    The replacement string, which can use groups from the regex if applicable.

                regex
                    Boolean indicating whether "from" is a regular expression.
