from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, Job
from telegram import KeyboardButton, ParseMode, ReplyKeyboardMarkup
import codecs
import json

import logging
logging.basicConfig(format="\n%(levelname)s: @'%(asctime)s' in '%(name)s':\n> %(message)s", level=logging.INFO)

import os
os.chdir("/home/zlyfer/TelegramBots/TelegramGetTelegramBetaBot/")

updater = Updater(token=open('token', 'r').readline())

tgrambetaapk_file = codecs.open('file_id', 'r')
global tgrambetaapk_file_id
tgrambetaapk_file_id = tgrambetaapk_file.readline()
tgrambetaapk_file.close

global language
language = {}
global langkeyboard
langkeyboard = []

def sys_updateapk(file_id):
    tgrambetaapk_file = codecs.open('file_id', 'w')
    tgrambetaapk_file.write(file_id)
    tgrambetaapk_file.close
    return

def sys_adduser(chat_id):
    users_file = codecs.open('users', 'r+', 'utf-8')
    users_file_content = users_file.readlines()
    exists = False
    for entry in users_file_content:
        if ' %s ' % chat_id in entry:
            exists = True
    if exists == False:
        users_file.write(' %s en-US\n' % chat_id)
    users_file.close
    return

def sys_updatelanguage(chat_id, language_code):
    users_file = codecs.open('users', 'r', 'utf-8')
    users_file_content = users_file.readlines()
    users_file.close
    users_file = codecs.open('users', 'w', 'utf-8')
    for entry in users_file_content:
        if str(chat_id) in entry:
            users_file.write(" %s %s\n" % (chat_id, language_code))
        else:
            users_file.write(entry)
    users_file.close
    return

def sys_getuserlanguage(chat_id):
    users_file = codecs.open('users', 'r', 'utf-8')
    users_file_content = users_file.readlines()
    users_file.close
    for entry in users_file_content:
        if ' %s ' % chat_id in entry:
            return (entry.split()[1])
    return (False)

def job_loadlanguages(bot, job):
    global language
    language = {}
    global langkeyboard
    langkeyboard = []
    for lang in os.listdir('lang'):
        langfile = codecs.open('lang/' + lang, 'r', 'utf-8')
        lang = lang.replace('.json', '')
        langdct = json.loads(langfile.readline())
        language[lang] = langdct
        language[lang]['lang_code'] = lang
        langkeyboard.append([KeyboardButton("%s %s" % (language[lang]['flag'], language[lang]['languagename']))])
        langfile.close
    return

def bot_start(bot, update):

    bot.send_chat_action(chat_id=update.message.chat_id, action='TYPING')
    bot.sendMessage(chat_id=-248828335, parse_mode="HTML", text="<strong>%s/%s/%s/%s</strong>: <i>%s</i>" % (update.message.chat.username, update.message.chat.first_name, update.message.chat_id, sys_getuserlanguage(update.message.chat_id), update.message.text))

    sys_adduser(update.message.chat_id)

    Greeting = ""
    for lang in language:
        Select = language[lang]['flag'] + " " + language[lang]['select'] + "\n"
        Greeting += Select
    update.message.reply_text(parse_mode='HTML', text=Greeting, reply_markup=ReplyKeyboardMarkup(langkeyboard))

    return

def bot_main(bot, update):

    bot.send_chat_action(chat_id=update.message.chat_id, action='TYPING')

    text = update.message.text
    chat_id = update.message.chat_id
    user_lang_code = sys_getuserlanguage(chat_id)
    user_lang = language[user_lang_code]
    username = update.message.chat.username
    first_name = update.message.chat.first_name

    bot.sendMessage(chat_id=-248828335, parse_mode="HTML", text="<strong>%s/%s/%s/%s</strong>: <i>%s</i>" % (username, first_name, chat_id, user_lang_code, text))

    for lang in language:
        if text == language[lang]['flag'] + " " + language[lang]['languagename']:
            sys_updatelanguage(chat_id, language[lang]['lang_code'])
            update.message.reply_text(parse_mode='HTML', text=language[lang]['start'], reply_markup=ReplyKeyboardMarkup([[KeyboardButton("%s" % language[lang]['button'])]]))
            return
        elif text == language[lang]['button']:
            bot.send_document(chat_id=chat_id, document=tgrambetaapk_file_id)
            update.message.reply_text(parse_mode='HTML', text=language[lang]['send'], reply_markup=ReplyKeyboardMarkup([[KeyboardButton("%s" % language[lang]['button'])]]))
            return

    update.message.reply_text(parse_mode='HTML', text=user_lang['unknown'])

    return

def bot_updateapk(bot, update):

    bot.send_chat_action(chat_id=update.message.chat_id, action='TYPING')

    chat_id = update.message.chat_id
    user_lang_code = sys_getuserlanguage(chat_id)
    user_lang = language[user_lang_code]
    username = update.message.chat.username
    first_name = update.message.chat.first_name

    if update.message.chat_id in [175576819]:
        global tgrambetaapk_file_id
        tgrambetaapk_file_id = update.message.document.file_id
        sys_updateapk(tgrambetaapk_file_id)
        update.message.reply_text(parse_mode='HTML', text=user_lang['file'] + "\n<strong>%s</strong>" % tgrambetaapk_file_id)
        bot.sendMessage(chat_id=-248828335, parse_mode='HTML', text="<strong>%s/%s/%s/%s</strong>: <i>FILE_ID:</i>\n<strong>%s</strong>" % (username, first_name, chat_id, user_lang_code, tgrambetaapk_file_id))
    else:
        update.message.reply_text(parse_mode='HTML', text=user_lang['denied'])
        bot.sendMessage(chat_id=-248828335, parse_mode='HTML', text="<strong>%s/%s/%s/%s</strong>: <i>File upload denied!</i>" % (username, first_name, chat_id, user_lang_code))

    return

updater.job_queue.run_repeating(job_loadlanguages, interval=86400, first=0)
updater.dispatcher.add_handler(CommandHandler('start', bot_start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, bot_main))
updater.dispatcher.add_handler(MessageHandler(Filters.document, bot_updateapk))

updater.start_polling()
updater.idle()
