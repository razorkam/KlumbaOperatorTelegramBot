import re
from . import Commands, TextSnippets, BitrixFieldMappings

MD_ESCAPE_PATTERN = re.compile('([*_`])')
BITRIX_DEAL_NUMBER_PATTERN = re.compile('^\\d+$')
COURIER_SETTING_COMMAND_PATTERN = re.compile('^' + Commands.SET_COURIER_PREFIX +
                                            Commands.SET_COURIER_DELIMETER + '\\d+$')

ADDRESS_LINK_RESOLVING_SPECIAL_CHARS_PATTERN = re.compile('["]')
BITRIX_ADDRESS_PATTERN = re.compile('(.+)\\|(\\d+\\.\\d+;\\d+\\.\\d+)')
BITRIX_DATE_PATTERN = re.compile('(\\d{4})-(\\d{2})-(\\d{2}).*')


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


def prepare_deal_address(obj, addrkey):
    val = prepare_external_field(obj, addrkey)

    val = re.sub(ADDRESS_LINK_RESOLVING_SPECIAL_CHARS_PATTERN, '', val)

    location_check = BITRIX_ADDRESS_PATTERN.search(val)

    if location_check:
        return location_check[1], location_check[2]

    # address, location
    return val, None


def prepare_deal_date(obj, datekey):
    val = prepare_external_field(obj, datekey)

    date_check = BITRIX_DATE_PATTERN.search(val)

    if date_check:
        return date_check[3] + '.' + date_check[2] + '.' + date_check[1]

    return val


def prepare_deal_time(obj, timekey):
    val = prepare_external_field(obj, timekey)

    if val in BitrixFieldMappings.DEAL_TIME_MAPPING:
        return BitrixFieldMappings.DEAL_TIME_MAPPING[val]
    else:
        return TextSnippets.FIELD_IS_EMPTY_PLACEHOLDER


def prepare_deal_incognito(obj, inckey):
    val = prepare_external_field(obj, inckey)

    if val in BitrixFieldMappings.DEAL_INCOGNITO_MAPPING:
        return BitrixFieldMappings.DEAL_INCOGNITO_MAPPING[val]
    else:
        return TextSnippets.FIELD_IS_EMPTY_PLACEHOLDER