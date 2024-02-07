from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, constants
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from Helper.stringHelper import escape_characters
from Model.Model import Acompanhamento, Empresa
from Repository.EmpresaRepository import EmpresaRepository
from Repository.AcompanhamentoRepository import AcompanhamentoRepository

from Logger.logger import get_logger
from Repository.UserRepository import UserRepository

loger = get_logger("Acompanhamentos", 'acompanhamentos.log')

INICIAL, AGUARDAR, FAZER_CADASTRO, DISPONIVEIS, CADASTRAR, LISTAR, DELETAR, EXECUTA_REMOCAO = range(8)

acompanhamentoRep = AcompanhamentoRepository()
empresaRep = EmpresaRepository()
userRep = UserRepository()


async def start_acompanhamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa e pergunta o que o usuário quer fazer."""
    reply_keyboard = [["Cadastrar Acompanhamento", "Ver o que já está acompanhando", "Apagar Acompanhamento"]]

    await update.message.reply_text(
        "Olá! Estou aqui para lhe ajudar a gerenciar como ficar de olho em empresas que entrem em promoção na livelo."
        "Digite /cancel para interromper a conversa a qualquer momento.\n\n"
        "O que você deseja fazer?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="O que deseja fazer?"
        ),
    )

    return AGUARDAR


async def aguardar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verifica qual foi o comando e passa para a próxima função."""
    user = update.message.from_user
    loger.info("Aguardar - Usuário %s: %s", user.full_name, update.message.text)
    passo = update.message.text
    if passo == "Cadastrar Acompanhamento":
        return await fazer_cadastro(update, context)
    elif passo == "Ver o que já está acompanhando":
        return await listar_cadastradas(update, context)
    elif passo == "Apagar Acompanhamento":
        return await deletar_acompanhamento(update, context)
    else:
        await update.message.reply_text(
            "Opção não reconhecida. Reiniciando.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END


async def fazer_cadastro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lista as empresas disponíveis para acompanhamento e aguarda input do usuário."""
    user = update.message.from_user
    loger.info("Cadastrar Acompanhamento (solicitar número do usuário) - Usuário %s: %s", user.full_name,
               update.message.text)
    disponiveis = __empresas_disponiveis__(update.effective_chat.id)
    lista = []

    txt = ("Você deseja cadastrar empresas para que eu fique de olho, certo? Segue uma lista de parceiros da livelo "
           "que posso ficar de olho para você.\nBasta digitar o número de cada empresa separado por vírgulas.\n Lista "
           "das empresas disponíveis:")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
    txt = ""
    count = 0
    for emp in disponiveis:
        txt_emp = f"{count + 1} - {emp.nome.upper()}"
        if len(txt) + len(txt_emp) >= constants.MessageLimit.MAX_TEXT_LENGTH:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
            txt = ""
        txt += txt_emp + "\n"
        count += 1
    await update.message.reply_text(txt, reply_markup=ReplyKeyboardRemove())
    return DISPONIVEIS


async def empresas_disponiveis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Pega lista das empresas pedidas pelo usuário."""
    user = update.message.from_user
    loger.info("Cadastrar Acompanhamento (realizando cadastro) - Usuário %s: %s", user.full_name, update.message.text)
    disponiveis = __empresas_disponiveis__(update.effective_chat.id)
    opcoes = set([x.strip() for x in update.message.text.split(",")])
    numericas = [int(x) for x in opcoes if x.isnumeric()]
    salvas = []
    for emp in numericas:
        if emp > len(disponiveis): continue
        empresa = disponiveis[emp - 1]
        usuario = userRep.getById(update.effective_chat.id)
        saving = AcompanhamentoRepository().save(user=usuario, empresa=empresa)
        if saving == True:
            salvas.append(empresa.nome.upper())
    await update.message.reply_text(
        f"Vou ficar de olho nas empresas a seguir por você:\n{', '.join(salvas)}\n"
        "Quando a pontuação de alguma delas entrar em oferta na Livelo, vou lhe avisar.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def listar_cadastradas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lista empresas com acompanhamento já cadastrado."""
    user = update.message.from_user
    loger.info("Listar Cadastradas do usuario %s", user.full_name)
    existentes = acompanhamentoRep.getByUserId(update.effective_chat.id)
    lista = []
    for existente in existentes:
        lista.append(existente.empresa.nome.upper())

    if len(lista) == 0:
        txt_lista = "Sem acompanhamentos encontrados"
    else:
        txt_lista = "\n".join(lista)
    await update.message.reply_text(
        f"Estou acompanhando as seguintes empresas para você:\n{txt_lista}"
    )

    return ConversationHandler.END


async def deletar_acompanhamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lista empresas com acompanhamento já cadastrado do usuário para deletar."""
    user = update.message.from_user
    loger.info("Listar Cadastradas do usuario para remoção %s", user.full_name)
    existentes = acompanhamentoRep.getByUserId(update.effective_chat.id)
    lista = []
    count = 0
    for acomp in existentes:
        lista.append(f"{count + 1} - {acomp.empresa.nome.upper()}")
        count += 1

    reply_keyboard = [[str(x) for x in list(range(1, count + 1))]]
    txt = ("Você deseja deixar de acompanhar quais empresas?\nBasta digitar o número de cada empresa separado por "
           "vírgulas. Lista das empresas acompanhadas:\n")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
    txt = ""
    count = 0
    for emp in lista:
        if len(txt) + len(emp) >= constants.MessageLimit.MAX_TEXT_LENGTH:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
            txt = ""
        txt += emp + "\n"
        count += 1
    await update.message.reply_text(txt, reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder="1, 2, 3, 4"
    ))

    return EXECUTA_REMOCAO


async def remover_acompanhamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Remove os acompanhamentos solicitados pelo usuário."""
    user = update.message.from_user
    loger.info("Cadastrar Acompanhamento (realizando cadastro) - Usuário %s: %s", user.full_name, update.message.text)
    existentes = acompanhamentoRep.getByUserId(update.effective_chat.id)
    opcoes = set([x.strip() for x in update.message.text.split(",")])
    numericas = [int(x) for x in opcoes if x.isnumeric()]
    apagadas = []
    for i in numericas:
        acompanhamento = existentes[i - 1]
        deleting = acompanhamentoRep.remove(acompanhamento)
        if deleting == True:
            apagadas.append(acompanhamento.empresa.nome.upper())
    await update.message.reply_text(
        f"Pronto, agora você não receberá mais mensagens quando surgirem promoções dessas empresas:\n{','.join(apagadas)}"
        ,
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    loger.info("User %s cancelou a conversa.", user.first_name)
    await update.message.reply_text(
        "Até mais! Espero poder lhe ajudar.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def get_acompanhamento_handler():
    # INICIAL, AGUARDAR, FAZER_CADASTRO, DISPONIVEIS, LISTAR, DELETAR, EXECUTA_REMOCAO = range(8)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("acompanhar", start_acompanhamento)],
        states={
            INICIAL: [CommandHandler("acompanhar", start_acompanhamento)],
            AGUARDAR: [MessageHandler(filters.TEXT & (~filters.COMMAND), aguardar)],
            FAZER_CADASTRO: [MessageHandler(filters.TEXT & (~filters.COMMAND), fazer_cadastro)],
            DISPONIVEIS: [MessageHandler(filters.TEXT & (~filters.COMMAND), empresas_disponiveis)],
            LISTAR: [MessageHandler(filters.TEXT & (~filters.COMMAND), listar_cadastradas)],
            DELETAR: [MessageHandler(filters.TEXT & (~filters.COMMAND), deletar_acompanhamento)],
            EXECUTA_REMOCAO: [MessageHandler(filters.TEXT & (~filters.COMMAND), remover_acompanhamento)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    return conv_handler


def __empresas_disponiveis__(chat_id: int):
    empresas = empresaRep.getAll()
    acompanhamentos = acompanhamentoRep.getByUserId(chat_id)
    codigos = [acomp.empresa.codigo for acomp in acompanhamentos]
    lista = []
    for empresa in empresas:
        if empresa.codigo not in codigos and empresa.codigo != "":
            lista.append(empresa)

    return lista
