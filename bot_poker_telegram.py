
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 👉 Coloque aqui seu Token do BotFather:
TOKEN = "7801066988:AAGicTGnR9SvIz6V0E20WbEgmULnGTdXRMg"


# Função de análise da mão pré-flop
def analisar_mao(carta1, carta2, suited):
    cartas_fortes = [('A', 'A'), ('K', 'K'), ('Q', 'Q'), ('J', 'J'), ('10', '10'),
                      ('A', 'K'), ('A', 'Q'), ('A', 'J'), ('K', 'Q')]

    par = carta1 == carta2

    if par and carta1 in ['A', 'K', 'Q', 'J', '10', '9', '8']:
        return "👉 RAISE - Par alto, jogue agressivo!"
    elif (carta1, carta2) in cartas_fortes or (carta2, carta1) in cartas_fortes:
        if suited:
            return "👉 RAISE - Conectores altos suited!"
        else:
            return "👉 CALL ou RAISE - Boa mão offsuited."
    else:
        conectores = ['A', 'K', 'Q', 'J', '10', '9', '8', '7']
        if carta1 in conectores and carta2 in conectores:
            if suited:
                return "👉 CALL - Conectores suited, chance de sequência ou flush."
            else:
                return "👉 CALL com cautela."
        else:
            return "👉 FOLD - Mão fraca, jogue fora."


# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '🃏 Bem-vindo ao Analista de Pôquer!\n\n'
        'Use o comando assim:\n'
        '/analisar A K suited\n\n'
        'Substitua A e K pelas suas cartas (A, K, Q, J, 10, 9...)\n'
        'e "suited" (mesmo naipe) ou "offsuit" (naipes diferentes).'
    )


# Comando /analisar
async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        carta1 = context.args[0].upper()
        carta2 = context.args[1].upper()
        suited = context.args[2].lower() == 'suited'

        resultado = analisar_mao(carta1, carta2, suited)

        await update.message.reply_text(
            f'🃏 Sua mão: {carta1} {carta2} {"♥️" if suited else "♠️"}\n\n{resultado}'
        )

    except Exception:
        await update.message.reply_text(
            "❌ Comando inválido.\n"
            "Exemplo correto:\n"
            "/analisar A K suited"
        )


# Construção do aplicativo do bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analisar", analisar))

print("🤖 Bot rodando...")
app.run_polling()
