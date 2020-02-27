from source import TextSnippets

CBQ_DELIM = '_'
DEALS_BUTTON_PREFIX = 'deals'
DEALS_BUTTON_PREV_DATA = 'prev'
DEALS_BUTTON_NEXT_DATA = 'next'
DEALS_NEXT_CBQ_DATA = DEALS_BUTTON_PREFIX + CBQ_DELIM + DEALS_BUTTON_NEXT_DATA
DEALS_PREV_CBQ_DATA = DEALS_BUTTON_PREFIX + CBQ_DELIM + DEALS_BUTTON_PREV_DATA
DEALS_PREV_BUTTON_OBJ = {'text': '<', 'callback_data': DEALS_PREV_CBQ_DATA}
DEALS_NEXT_BUTTON_OBJ = {'text': '>', 'callback_data': DEALS_NEXT_CBQ_DATA}

TO_MAIN_MENU_CALLBACK_DATA = 'mainmenu'
TO_MAIN_MENU_BUTTON_OBJ = {'inline_keyboard':
                               [[{'text': TextSnippets.TO_MAIN_MENU_BUTTON_TEXT,
                                  'callback_data': TO_MAIN_MENU_CALLBACK_DATA}]]}

TO_DEALS_CALLBACK_DATA = 'todeals'
TO_DEALS_BUTTON_OBJ = {'inline_keyboard':
                           [[{'text': TextSnippets.TO_DEALS_BUTTON_TEXT,
                              'callback_data': TO_DEALS_CALLBACK_DATA}]]}

REFRESH_DEALS_BUTTON_OBJ = {'inline_keyboard':
                                [[{'text': TextSnippets.REFRESH_DEALS_BUTTON_TEXT,
                                   'callback_data': TO_DEALS_CALLBACK_DATA}]]}

CLOSE_DEAL_CALLBACK_PREFIX = 'closedeal'
CLOSE_DEAL_DIALOG_BUTTON_OBJ = {'inline_keyboard':
                                    [[{'text': TextSnippets.DEAL_CLOSING_DIALOG_YES,
                                       'callback_data': CLOSE_DEAL_CALLBACK_PREFIX}],
                                     [{'text': TextSnippets.TO_DEALS_BUTTON_TEXT,
                                       'callback_data': TO_DEALS_CALLBACK_DATA}]
                                     ]}
