import asyncio
import threading
import traceback
from time import sleep

import schedule
from telegram import Update, constants
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

from Helper.stringHelper import escape_characters
from Logger.logger import get_logger
from Model.Model import User
from Repository.AcompanhamentoRepository import AcompanhamentoRepository
from Repository.ParceriaRepository import ParceriaRepository
from Repository.UserRepository import UserRepository
from cadastro_acompanhamento import get_acompanhamento_handler
from extract_empresas import extractEmpresas
from extract_parcerias import extract_parcerias
from read_parcerias import get_ofertas

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
fileLoger = get_logger("TelegramBOT", "telegram.log")
errorLogger = get_logger("Errors", "errors.log")
httoLogger = get_logger("httpx", "httpx.log")
acompanhamentoLogger = get_logger("Acompanhamentos", "acompanhamentos.log")
token = open("token.txt", "r").read()

application = None


def run_schedule():
    while True:
        schedule.run_pending()
        sleep(60)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.effective_message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Desculpe, o comando {command} não existe.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    errorLogger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    # message = (
    #     "An exception was raised while handling an update\n"
    #     f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
    #     "</pre>\n\n"
    #     f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
    #     f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
    #     f"<pre>{html.escape(tb_string)}</pre>"
    # )
    #
    #
    # # Finally, send the message
    #
    # await context.bot.send_message(
    #
    #     chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    #
    # )


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


def avisaAcompanhamento():
    repo = AcompanhamentoRepository()
    acompanhamentos = repo.getAcompanhamentosComOfertas()
    parcerias = get_ofertas()

    loop = asyncio.new_event_loop()
    for parceria in parcerias:
        acompanhando = list(filter(lambda x: x.empresa.id == parceria.empresa.id, acompanhamentos))
        for acompanhamento in acompanhando:
            if acompanhamento.ultima_informacao is None or acompanhamento.ultima_informacao < parceria.inicio:
                try:
                    acompanhamentoLogger.info(f"Registrando oferta em {parceria.empresa.nome} para @{acompanhamento.user.username}")
                    result = loop.run_until_complete(application.bot.send_message(chat_id=acompanhamento.user.chat_id,
                                                                                  text=escape_characters(
                                                                                      f"{parceria.empresa.nome.upper()} acabou de "
                                                                                      f"entrar em oferta: {parceria.toMarkdown()}"),
                                                                                  parse_mode=constants.ParseMode.MARKDOWN_V2))
                    repo.registerEnvio(acompanhamento)
                except Exception as ex:
                    acompanhamentoLogger.error(ex)


async def addUser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    [chat_id, name, last_name, username] = [update.effective_chat.id, update.effective_chat.first_name,
                                            update.effective_chat.last_name, update.effective_chat.username]
    u = User()
    u.chat_id = chat_id
    u.last_name = last_name
    u.first_name = name
    u.username = username
    userRepository = UserRepository()
    userRepository.save(u)


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).read_timeout(30).write_timeout(30).build()
    start_handler = CommandHandler('start', start)
    oferta_handler = CommandHandler('ofertas', ofertas)
    acompanhamento_handler = get_acompanhamento_handler()
    add_user_handler = MessageHandler(filters.ALL, addUser)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_error_handler(error_handler)
    application.add_handler(start_handler)
    application.add_handler(acompanhamento_handler)
    application.add_handler(add_user_handler, 1)
    application.add_handler(oferta_handler)
    application.add_handler(unknown_handler)
    schedule.every(20).minutes.do(extract_parcerias)
    schedule.every(10).minutes.do(avisaAcompanhamento)
    schedule.every().day.at("06:00").do(extractEmpresas)
    t = threading.Thread(target=run_schedule)
    t.start()
    application.run_polling(timeout=30)
