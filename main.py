#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
DEFAULT TEMPLATE

STRUCTURE:
    - main.py               ~ (entry point) Setting all handlers/controllers, etc (current file)
    - base.py               ~ Reading values.json file, setting config, texts, keyboards, inline vars. (logger)
    - base_h.py             ~ Base bot's handlers (to_main, bug_report)
    - database.py           ~ peewee classes for communication with database

    - commands_h.py         ~ Defult commands handlers (/start, /info) (adding other commands here too)

    - functions.py          ~ Custom function for specific bot (scrapers, api wrappers, etc)
    - test_handlers.py      ~ Custom handlers for custom menus, commands, navigation (1 button hendler, for tests)

    - database.db           ~ SQLite database for dev process (Postgresql on production)
    - config.json           ~ All projects configs, api keys, tokens, etc
    - values.json           ~ All bot's texts and keyboards, for different languages

Developer: Alexander Machek [@youbrain]
Repository: https://github.com/s404s/bot_ecosystem/tree/dev/organaizer

TODO:
    - all dev tasks here
'''
from telegram import ParseMode
from telegram.ext import (Updater, Filters, Defaults)
from telegram.ext import (CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler)

from base import *
from base_h import (to_main, to_dashboard, to_main_with_msg_del, check_other_text)

from commands_h import (info, start, access)
from dashboard_h import statistics
from settings_h import (settings, set_sth, pswd_set, edit_pswd, set_lockation_txt, set_locatipn_geo, set_coords)
from bug_report_h import (bug_report, bugrep_text, report_other, rem_part_report, send_report)

from test_handlers import button


def main():
    '''ENTRY POINT'''
    updater = Updater(config['bot_token'], use_context=True, defaults=Defaults(parse_mode=ParseMode.HTML))
    dp = updater.dispatcher

    # Conversation Handlers
    bug_report_h = ConversationHandler( # BUG REPORT 
        entry_points=[CallbackQueryHandler(bug_report, pattern="bug_report")],
        states={
            SEND_BUGREP_TXT:   [CallbackQueryHandler(to_main_with_msg_del, pattern="bug_rep_cancel"), # cancel report
                                MessageHandler(Filters.text, bugrep_text)], # get a report text

            SEND_BUGREP_OTHER: [CallbackQueryHandler(to_main_with_msg_del, pattern="bug_rep_cancel"), # cancel report
                                CallbackQueryHandler(rem_part_report, pattern="bug_rep_delp_"), # remove part of report
                                CallbackQueryHandler(send_report, pattern="bug_rep_send"), # send report
                                MessageHandler(Filters.all, report_other)]
        },
        fallbacks=[],
        per_message=False
    )

    dash_h = ConversationHandler( # DASHBOARD 
        entry_points=[CommandHandler("dashboard", to_dashboard)],
        states={
            DASH_MAIN:   [MessageHandler(Filters.regex(f"^({keyboards['dashboard']['menu'][0][0]})$"), statistics)], # statistics btn

            DASH_STAT:   [MessageHandler(Filters.regex(f"^({keyboards['dashboard']['statistics'][0][0][0]})$"), to_dashboard)] # back
        },
        fallbacks=[],
        per_message=False
    )

    settings_h = ConversationHandler( # SETTINGS
        entry_points=[MessageHandler(Filters.regex(f"^({keyboards['main'][0][0]})$"), settings)],
        states={
            SETTINGS_MAIN: [CallbackQueryHandler(to_main_with_msg_del, pattern="to_main"),
                            CallbackQueryHandler(set_sth, pattern="set_"),
                            CallbackQueryHandler(pswd_set, pattern="password_set")],
            SET_PSWD:      [MessageHandler(Filters.text, edit_pswd)],
            SET_LOCATION:  [MessageHandler(Filters.text, set_lockation_txt),
                            MessageHandler(Filters.location, set_locatipn_geo),
                            CallbackQueryHandler(set_coords, pattern="set_coords_")]
        },
        fallbacks=[],
        per_message=False
    )

    # commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("info", info))

    # Cconversations
    dp.add_handler(dash_h)
    dp.add_handler(bug_report_h)
    dp.add_handler(settings_h)

    dp.add_handler(CallbackQueryHandler(access, pattern="access_"))
    dp.add_handler(MessageHandler(Filters.text, check_other_text))
    # errors
    # dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
