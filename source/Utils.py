import re
from . import Commands, TextSnippets

MD_ESCAPE_PATTERN = re.compile('([*_`])')
BITRIX_DEAL_NUMBER_PATTERN = re.compile('^\\d+$')
COURIER_SETTING_COMMAND_PATTERN = re.compile('^' + Commands.SET_COURIER_PREFIX +
                                            Commands.SET_COURIER_DELIMETER + '\\d+$')


def get_field(obj, key):
    if key in obj:
        return obj[key]
    else:
        return None


def escape_markdown_special_chars(str):
    return re.sub(MD_ESCAPE_PATTERN, r'\\\g<1>', str)


def _stringify_field(field):
    if field in (False, None, {}, []):
        return TextSnippets.FIELD_IS_EMPTY_PLACEHOLDER
    else:
        return field

def prepare_external_field(obj, key):
    val = get_field(obj, key)

    if type(val) is list:
        val = ', '.join(val)

    return escape_markdown_special_chars(_stringify_field(val))


def is_deal_number(command):
    return BITRIX_DEAL_NUMBER_PATTERN.match(command)


def is_courier_setting_command(command):
    return COURIER_SETTING_COMMAND_PATTERN.match(command)