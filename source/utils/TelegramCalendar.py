from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime
import calendar

TIMES_ROW_SIZE = 6
TIMES_LIST = [
    '00:00',
    '01:00',
    '02:00',
    '03:00',
    '04:00',
    '05:00',
    '06:00',
    '07:00',
    '08:00',
    '09:00',
    '10:00',
    '11:00',
    '12:00',
    '13:00',
    '14:00',
    '15:00',
    '16:00',
    '17:00',
    '18:00',
    '19:00',
    '20:00',
    '21:00',
    '22:00',
    '23:00'
]

PATTERN = '^.+$'


class State:
    IGNORE = 'IGNORE'
    DAY = 'DAY'
    HOUR = 'HOUR'
    PREV_MONTH = 'PREV_MONTH'
    NEXT_MONTH = 'NEXT_MONTH'


def create_callback_data(action, year, month, day, hour):
    return ";".join([action, str(year), str(month), str(day), str(hour)])


def separate_callback_data(data):
    return data.split(";")


def create_calendar(year=None, month=None):
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    data_ignore = create_callback_data(State.IGNORE, year, month, 0, 0)
    keyboard = []
    # First row - Month and Year
    row = []

    with calendar.different_locale('ru_RU.UTF-8'):
        row.append(InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data=data_ignore))

    keyboard.append(row)
    # Second row - Week Days
    row = []
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        row.append(InlineKeyboardButton(day, callback_data=data_ignore))
    keyboard.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=create_callback_data(State.DAY, year, month, day,
                                                                                             0)))
        keyboard.append(row)
    # Last row - Buttons
    row = [InlineKeyboardButton("<", callback_data=create_callback_data(State.PREV_MONTH, year, month, day, 0)),
           InlineKeyboardButton(" ", callback_data=data_ignore),
           InlineKeyboardButton(">", callback_data=create_callback_data(State.NEXT_MONTH, year, month, day, 0))]

    keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def create_timesheet(year, month, day):
    keyboard = []
    row = []

    for i, t in enumerate(TIMES_LIST):
        if row and i % TIMES_ROW_SIZE == 0:
            keyboard.append(row)
            row = []

        row.append(InlineKeyboardButton(t, callback_data=create_callback_data(State.HOUR, year, month, day, i)))

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def process_calendar_selection(update, context):
    ret_data = (False, None)
    query = update.callback_query

    (action, year, month, day, hour) = separate_callback_data(query.data)
    curr = datetime.datetime(int(year), int(month), 1)
    if action == State.IGNORE:
        context.bot.answer_callback_query(callback_query_id=query.id)
    elif action == State.DAY:
        context.bot.edit_message_text(text=query.message.text,
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=create_timesheet(int(year), int(month), int(day))
                                      )
    elif action == State.HOUR:
        context.bot.edit_message_text(text=query.message.text,
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id
                                      )
        ret_data = True, datetime.datetime(int(year), int(month), int(day), int(hour))
    elif action == State.PREV_MONTH:
        pre = curr - datetime.timedelta(days=1)
        context.bot.edit_message_text(text=query.message.text,
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=create_calendar(int(pre.year), int(pre.month)))
    elif action == State.NEXT_MONTH:
        ne = curr + datetime.timedelta(days=31)
        context.bot.edit_message_text(text=query.message.text,
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=create_calendar(int(ne.year), int(ne.month)))
    else:
        context.bot.answer_callback_query(callback_query_id=query.id, text="Something went wrong!")
        # UNKNOWN
    return ret_data
