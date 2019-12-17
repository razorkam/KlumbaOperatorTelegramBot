import re
import TextSnippets
import Commands

MD_ESCAPE_PATTERN = re.compile('([*_`])')
DEAL_ACTION_COMMAND_PATTERN = re.compile(Commands.DEAL_OPEN_PREFIX + TextSnippets.DEAL_ACTION_DELIM + '|'
                                         + Commands.DEAL_CLOSE_PREFIX + TextSnippets.DEAL_ACTION_DELIM + '*')


def escape_markdown_special_chars(str):
    return re.sub(MD_ESCAPE_PATTERN, r'\\\1', str)


def _stringify_field(field):
    if field in (False, None, {}, []):
        return TextSnippets.FIELD_IS_EMPTY_PLACEHOLDER
    else:
        return field


def prepare_external_field(field):
    if type(field) is list:
        field = ','.join(field)

    return escape_markdown_special_chars(_stringify_field(field))


def is_deal_action(command):
    return DEAL_ACTION_COMMAND_PATTERN.match(command)