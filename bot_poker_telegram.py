
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import random
from collections import Counter

TOKEN = os.getenv(7801066988:AAGicTGnR9SvIz6V0E20WbEgmULnGTdXRMg)

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

def simular_monte_carlo(mao, mesa, n_oponentes=5, simulacoes=50000):
    baralho = [v + n for v in valores_ordem.keys() for n in naipes]
    usadas = mao + mesa
    for c in usadas:
        baralho.remove(c)

    vitoria = empate = derrota = 0

    for _ in range(simulacoes):
        restante = baralho.copy()
        random.shuffle(restante)

        oponentes = [restante[i*2:(i+1)*2] for i in range(n_oponentes)]
        restante = restante[n_oponentes*2:]

        cartas_mesa = mesa + restante[:max(0, 5-len(mesa))]

        nossa_mao = mao + cartas_mesa
        mao_nossa, _ = avaliar_mao(nossa_mao)

        resultados_oponentes = []
        for op in oponentes:
            mao_oponente = op + cartas_mesa
            mao_op, _ = avaliar_mao(mao_oponente)
            resultados_oponentes.append(mao_op)

        if all(mao_nossa >= r for r in resultados_oponentes):
            vitoria += 1
        elif any(mao_nossa < r for r in resultados_oponentes):
            derrota += 1
        else:
            empate += 1

    total = vitoria + empate + derrota
    return (vitoria/total*100, empate/total*100, derrota/total*100)

async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE, etapa: str) -> None:
    try:
        cartas = [c.upper() for c in context.args]
        if etapa == "flop" and len(cartas) != 5:
            raise ValueError
        if etapa == "turn" and len(cartas) != 6:
            raise ValueError
        if etapa == "river" and len(cartas) != 7:
            raise ValueError

        mao = cartas[0:2]
        mesa = cartas[2:]
        total_cartas = mao + mesa

        mao_nome, sugestao = avaliar_mao(total_cartas)
        vitoria, empate, derrota = simular_monte_carlo(mao, mesa)

        await update.message.reply_text(
            f'🃏 Sua mão: {cartas}\n\n👉 Resultado: {mao_nome}\n👉 Sugestão: {sugestao}\n'
            f'🎲 Probabilidade de Vitória: {vitoria:.2f}%\n'
            f'🎲 Empate: {empate:.2f}%\n'
            f'🎲 Derrota: {derrota:.2f}%'
        )

    except:
        await update.message.reply_text(f"❌ Uso incorreto. Exemplo correto: /analisar_{etapa} AH KH 8C QD 3S")

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
app.add_handler(CommandHandler("analisar_flop", lambda u, c: analisar(u, c, "flop")))
app.add_handler(CommandHandler("analisar_turn", lambda u, c: analisar(u, c, "turn")))
app.add_handler(CommandHandler("analisar_river", lambda u, c: analisar(u, c, "river")))

print("🤖 Bot rodando...")
app.run_polling()
