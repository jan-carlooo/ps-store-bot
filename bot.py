import os
import re
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://store.playstation.com/pt-br/pages/deals"

def buscar_ofertas():
    resposta = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    soup = BeautifulSoup(resposta.text, "html.parser")
    texto = soup.get_text(" ", strip=True)

    ofertas = []

    # Procura blocos de texto contendo descontos
    padrao = re.compile(
        r"(.{5,120}?)\s+(?:PS4|PS5 PS4)\s+.*?-(\d+)%\s+R\$([\d.,]+)",
        re.I
    )

    for nome, desconto, preco in padrao.findall(texto):
        desconto = int(desconto)

        if desconto > 50:
            ofertas.append(
                f"🎮 {nome.strip()}\n"
                f"🔥 {desconto}% OFF\n"
                f"💰 R$ {preco}\n"
            )

    return ofertas


def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": mensagem
        },
        timeout=30
    )


ofertas = buscar_ofertas()

if ofertas:
    mensagem = "🔥 OFERTAS PS4 COM MAIS DE 50% DE DESCONTO 🔥\n\n"
    mensagem += "\n".join(ofertas[:20])
    mensagem += "\n\n🛒 PlayStation Store Brasil"

    enviar_telegram(mensagem)
