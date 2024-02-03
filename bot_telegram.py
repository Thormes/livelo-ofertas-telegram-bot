import logging
from Logger.logger import get_logger
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, constants
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, InlineQueryHandler

from Model.Model import User, Acompanhamento
from read_parcerias import get_parcerias, get_ofertas
from Repository.UserRepository import UserRepository
from Repository.AcompanhamentoRepository import AcompanhamentoRepository

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
fileLoger = get_logger("TelegramBOT", "telegram.log")
httoLogger = get_logger("httpx", "httpx.log")
token = open("token.txt", "r").read()


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.effective_message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Desculpe, o comando {command} não existe.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Digite /ofertas para verificar as ofertas disponíveis na livelo para pontuação em compras")


async def ofertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fileLoger.info(f"Pedido de ofertas recebido: {update.effective_chat.full_name} - {update.effective_chat.id}")
    ofertas = get_ofertas()
    temp = sorted(ofertas, key=lambda x: x.empresa.nome)
    ofertas = sorted(temp, key=lambda x: x.inicio, reverse=True)
    txt = ""
    for oferta in ofertas:
        if len(txt) + len(oferta.toMarkdown()) >= constants.MessageLimit.MAX_TEXT_LENGTH:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=txt,
                                           parse_mode=constants.ParseMode.MARKDOWN_V2)
            txt = ""
        txt += escape_characters(oferta.toMarkdown()) + "\n\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=txt,
                                   parse_mode=constants.ParseMode.MARKDOWN_V2)


async def addUser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    [chat_id, name, last_name] = [update.effective_chat.id,update.effective_chat.first_name, update.effective_chat.last_name]
    u = User()
    u.chat_id = chat_id
    u.last_name = last_name
    u.first_name = name
    userRepository = UserRepository()
    userRepository.save(u)


def escape_characters(text: str) -> str:
    return text.replace(".", "\.").replace("(", "\(").replace(")", "\)").replace("-", "\-").replace("/", "\/").replace(
        ":", "\:")


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    start_handler = CommandHandler('start', start)
    oferta_handler = CommandHandler('ofertas', ofertas)
    add_user_handler = MessageHandler(filters.ALL, addUser)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(start_handler)
    application.add_handler(add_user_handler,1)
    application.add_handler(oferta_handler)
    application.add_handler(unknown_handler)
    application.run_polling(timeout=30)
