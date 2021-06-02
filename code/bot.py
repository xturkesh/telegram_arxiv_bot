import os 
from asyncio import run 
from parser import ArxivParser

from config import *

from telegram import (    ParseMode,
                          Update, 
                          InlineKeyboardButton, 
                          InlineKeyboardMarkup)
from telegram.ext import (  CallbackQueryHandler,
                            Updater, 
                            CommandHandler, 
                            MessageHandler,
                            Filters)

class ArxivSearchBot(ArxivParser,Updater):
    def __init__(self,*args,**kwargs):
        ArxivParser.__init__(self,*args,**kwargs)
        Updater.__init__(self,*args,**kwargs)

        self.count = 0
        self.message_array = []
        self.user_kw = set()
        self.user_archive = set()

        self.dispatcher.add_handler(CommandHandler("start"  , self.start))
        self.dispatcher.add_handler(CommandHandler("help"   , self.start))
        self.dispatcher.add_handler(CommandHandler("list"   , self.list_))
        self.dispatcher.add_handler(CommandHandler("add"    , self.add))
        self.dispatcher.add_handler(CommandHandler("remove" , self.remove,))
        self.dispatcher.add_handler(CommandHandler("get"    , self.get_news))
        self.dispatcher.add_handler(CommandHandler("archive", self.edit_archives))

        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.default))
        self.dispatcher.add_handler(CallbackQueryHandler(self.button))

    def start(self,update,context):
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id = chat_id,
                                 text = START,
                                 parse_mode = ParseMode.MARKDOWN)

    def list_(self,update,context):
        chat_id = update.message.chat_id
        usr_kw  = self.user_kw
        usr_arx = self.user_archive

        if len(usr_kw):
            key_list = ['*{}*'.format(k) for k in usr_kw]
            message = "The following is the list of keywords: "+', '.join(key_list)+'.\n'
            context.bot.send_message(chat_id=chat_id, 
                         text=message,
                         parse_mode=ParseMode.MARKDOWN)
        else:
            context.bot.send_message(chat_id=chat_id, 
                         text='Empty list of keywords.\n',
                         parse_mode=ParseMode.MARKDOWN)
        if len(usr_arx):
            arx_list =  ['-- _{}_\n'.format(k) for k in usr_arx]
            message = "I look in the following arxivs:\n"+ ''.join(arx_list)
            context.bot.send_message(chat_id=chat_id,
                         text=message,
                         parse_mode=ParseMode.MARKDOWN)
        else:
            context.bot.send_message(chat_id=chat_id,
                         text='Empty list of arxivs! Add with /archive command.\n',
                         parse_mode=ParseMode.MARKDOWN)

    def add(self,update,context):
        chat_id = update.message.chat_id
        message = ['The following words are added:\n']
        args = context.args
        if len(args):
            for k in args:
                kw = k.lower().replace("+", " ")
                self.user_kw.add(kw)
                message.append('- {}\n'.format(kw))
            context.bot.send_message(chat_id=update.message.chat_id,
                        text = ''.join(message),
                        parse_mode = ParseMode.MARKDOWN,)
        else:
            help_text=( "*Usage:*"
                        "`/add + KEYWORD(S)`\n"
                        "For connected words, use underscore +\n\n"
                        "Examples:\n"
                        "  1. : `/add entanglement`\n"
                        "       Add *'entanglement'* to the keywords.\n"
                        "  2. : `/add many-body monte+carlo electron`\n"
                        "       Add *'many-body'* *'monte carlo'* *'electron'* to the keywords."
                       )
            context.bot.send_message(chat_id=chat_id,
                        text = help_text,
                        parse_mode = ParseMode.MARKDOWN,)

    def remove(self,update,context):
        chat_id = update.message.chat_id
        message = ['The following words are removed:\n']
        args = context.args
        if 'ALL' in args:
            self.user_kw = set()
        elif len(args)>0:
            for k in args:
                kw = k.lower().replace("+",' ')
                self.user_kw.remove(kw)
                message.append('- {}\n'.format(kw))
            context.bot.send_message(chat_id=chat_id,
                            text = ''.join(message),
                            parse_mode = ParseMode.MARKDOWN,)
        else:
            help_text=( "*Usage:*"
                        "`/remove + KEYWORD(S)`\n"
                        "For connected words, use underscore +\n\n"
                        "Examples:\n"
                        "  1. : `/remove entanglement`\n"
                        "       Remove *'entanglement'* from the keywords.\n"
                        "  2. : `/remove many-body monte+carlo electron`\n"
                        "       Remove *'many-body'* *'monte carlo'* *'electron'* from the keywords.\n"
                        "  3. : `/remove ALL` (Case sensitive)\n"
                        "       Empty the list."
                        )
            context.bot.send_message(chat_id=chat_id,
                            text = help_text,
                            parse_mode = ParseMode.MARKDOWN,
                            )

    def edit_archives(self,update,context):
        keyboard = [[InlineKeyboardButton(key,callback_data=key) ] for key in self.archives.keys()]
        keyboard += [[InlineKeyboardButton('REMOVE ALL',callback_data='RM') ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Select all ArxiVs of interest:', reply_markup=reply_markup)

    def button(self,update,context):
        query = update.callback_query
        content = update.callback_query.message
        chat_id = content.chat_id
        message = content.message_id
        query_data = str(query.data)
        if (query_data=='RM'):
            self.user_archive = set()
            context.bot.edit_message_text(text="Arxiv cleared!\n",
                          chat_id=chat_id,
                          message_id=message)
        elif query_data in self.archives:
            arx = self.archives[query_data]
            self.user_archive.add(arx)
            context.bot.edit_message_text(text="Arxiv {} added!\n".format(query_data),
                          chat_id=chat_id,
                          message_id=message)
        else:
            query.answer()
            if (query.data=='<' and self.count>=1):
                self.count-= 1
            elif (query.data=='>') and self.count<= len(self.message_array):
                self.count+= 1
            elif (query.data=='<<'):
                self.count= 0
            elif (query.data=='>>'):
                self.count= len(self.message_array)-1
            query.edit_message_text(text=self.message_array[self.count],
                parse_mode = ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup =  SEARCH_MARKUP,)

    def filter_kw(self,items,abstracts,kw):
        user_news = []
        for item,abstract in zip(items,abstracts):
            if any([key.lower() in abstract for key in kw]):
                user_news.append(item)
        return user_news

    def entry_to_message(self,items,N = 20):
        message_array = []
        for k,item in enumerate(items):
            message = ''
            date = item['date']
            title = f'{k+1}. - ' +item['title']
            author = item['author']
            url = item['pdf_url']
            biburl = url.replace('/pdf/','/bibtex/')
            message+= ( f'*{title}*\n'
                        f'_{author}_ \n'
                        f'Appeared: {date}\t\t'
                        f'\U0001F4F0 [arXiv]({url})\t\t'
                        f'\U0001F4D6 [bibtex]({biburl})\t\t'
                        )
            if ('doi' in item):
                doi = item['doi']
                message+= f'\U0001F4D9 [DOI]({os.path.join(DOI,doi)})\n\n\n'
            else:
                message+= '\n\n\n'
            message_array.append(message)
        message_array = [''.join(message_array[n:n+N]) for n in range(0, len(message_array), N)]
        return message_array

    def get_news(self,update,context, N=20):
        chat_id = update.message.chat_id
        usr_kw = self.user_kw
        arxs = [self.path + arx for arx in self.user_archive]
        urls_arx = run(self.fetch_all(arxs, 'url',
                        callback = lambda items,abstracts: self.filter_kw(items,abstracts,usr_kw)))
        urls = []
        for url_list in urls_arx:
            urls.extend(url_list)
        urls = list(set(urls))
        entry_all = run(self.fetch_all(urls,'item',))
        messages_all = self.entry_to_message(entry_all)

        if (len(messages_all)):
            messages = [TITLE.format(k+1)+message for k,message in enumerate(messages_all)]
            for message in messages:
                context.bot.send_message(chat_id=chat_id,
                            text = message,
                            parse_mode=ParseMode.MARKDOWN,
                             disable_web_page_preview=True)
        else:
            context.bot.send_message(chat_id=chat_id,
                            text = '*No new papers for your keywords!*\n',
                            parse_mode=ParseMode.MARKDOWN,
                             disable_web_page_preview=True)

    def default(self,update,context):
        query = update.message.text
        urls = self.fetch_query(*(query.split()))
        if (len(urls)>=100):
            update.message.reply_text(text='*Too many results: Use better keywords.*',parse_mode=ParseMode.MARKDOWN,)
        elif (len(urls)==0):
            update.message.reply_text(text='*No results.*',parse_mode=ParseMode.MARKDOWN,)
        else:
            try:
                items = run(self.fetch_all(urls,'item'))

                self.message_array = self.entry_to_message(items,N=5)
                self.count = 0 
                
                update.message.reply_text(text=self.message_array[self.count],
                    disable_web_page_preview=True,
                    parse_mode = ParseMode.MARKDOWN,
                    reply_markup =  SEARCH_MARKUP,
                    )
            except Exception as e:
                print(f'Running Default Exception: {str(e)}')

if __name__ == '__main__':
    bot = ArxivSearchBot(token=TOKEN,)
    bot.start_polling()