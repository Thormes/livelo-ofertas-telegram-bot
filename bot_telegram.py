import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, constants
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, InlineQueryHandler
from read_parcerias import get_parcerias, get_ofertas

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

token = open("token.txt", "r").read()

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Desculpe, o comando não existe.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Digite /ofertas para verificar as ofertas disponíveis na livelo para pontuação em compras")


async def ofertas(update:Update, context: ContextTypes.DEFAULT_TYPE):
    ofertas = get_ofertas()
    txt = ""
    for oferta in ofertas:
        if len(txt) + len(str(oferta)) >= constants.MessageLimit.MAX_TEXT_LENGTH:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=txt, parse_mode=constants.ParseMode.MARKDOWN_V2)
            txt=""
        txt += escape_characters(str(oferta)) + "\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=txt, parse_mode=constants.ParseMode.MARKDOWN_V2)

def escape_characters(text: str) -> str:
    return text.replace(".", "\.").replace("(", "\(").replace(")","\)").replace("-", "\-").replace("/", "\/")


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    start_handler = CommandHandler('start', start)
    oferta_handler = CommandHandler('ofertas', ofertas)
    application.add_handler(oferta_handler)
    application.add_handler(start_handler)
    application.run_polling()
