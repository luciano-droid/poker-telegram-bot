
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import random
from collections import Counter

# Token do BotFather vindo da variável de ambiente
TOKEN = os.getenv('TOKEN')

valores_ordem = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                 '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

naipes = ['H', 'S', 'D', 'C']

def avaliar_mao(cartas):
    valores = [c[:-1] for c in cartas]
    naipes_cartas = [c[-1] for c in cartas]

    contagem = Counter(valores)
    counts = list(contagem.values())

    pares = counts.count(2)
    trincas = counts.count(3)
    quadras = counts.count(4)

    flush = any(naipes_cartas.count(n) >= 5 for n in set(naipes_cartas))

    valores_numericos = sorted(set([valores_ordem[v] for v in valores]))
    sequencia = False
    for i in range(len(valores_numericos) - 4 + 1):
        if valores_numericos[i + 4] - valores_numericos[i] == 4 and                 len(set(valores_numericos[i:i + 5])) == 5:
            sequencia = True

    straight_flush = False
    if flush:
        for n in set(naipes_cartas):
            naipe_valores = [valores_ordem[v] for v, s in zip(valores, naipes_cartas) if s == n]
            naipe_valores = sorted(set(naipe_valores))
            for i in range(len(naipe_valores) - 4 + 1):
                if naipe_valores[i + 4] - naipe_valores[i] == 4 and                         len(set(naipe_valores[i:i + 5])) == 5:
                    straight_flush = True

    if straight_flush and max(valores_numericos) == 14:
        return "Royal Flush", "RAISE - Melhor mão possível!"
    if straight_flush:
        return "Straight Flush", "RAISE - Mão extremamente forte!"
    if quadras == 1:
        return "Quadra", "RAISE - Mão muito forte!"
    if trincas == 1 and pares >= 1:
        return "Full House", "RAISE - Mão excelente!"
    if flush:
        return "Flush", "RAISE - Muito forte!"
    if sequencia:
        return "Sequência (Straight)", "CALL ou RAISE - Sequência é forte."
    if trincas == 1:
        return "Trinca", "CALL ou RAISE - Boa mão."
    if pares == 2:
        return "Dois Pares", "CALL - Jogue com cautela."
    if pares == 1:
        return "Par", "CALL - Par simples."
    return "Carta Alta", "FOLD - Mão fraca."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '🃏 Bem-vindo ao Analista de Pôquer!\n\n'
        'Comandos:\n'
        '/analisar_flop AH KH 8C QD 3S\n'
        '/analisar_turn AH KH 8C QD 3S 7H\n'
        '/analisar_river AH KH 8C QD 3S 7H KS\n'
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

print("🤖 Bot rodando...")
app.run_polling()
