import os
import json
import re
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

STORE_URL = "https://store.playstation.com/pt-br/pages/deals"
ARQUIVO_OFERTAS = "ofertas_enviadas.json"


def carregar_enviadas():
    try:
        with open(ARQUIVO_OFERTAS, "r", encoding="utf-8") as arquivo:
            return set(json.load(arquivo))
    except:
        return set()


def salvar_enviadas(ofertas):
    with open(ARQUIVO_OFERTAS, "w", encoding="utf-8") as arquivo:
        json.dump(list(ofertas), arquivo, ensure_ascii=False)


def buscar_ofertas():
    resposta = requests.get(
        STORE_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 13) "
                "AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
        timeout=30,
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, "html.parser")
    texto = soup.get_text(" ", strip=True)

    ofertas = []

    # Procura blocos que indiquem PS4 e desconto
    padrao = re.compile(
        r"(.{3,150}?)"
        r"(?:PS5\s+)?PS4"
        r".{0,120}?"
        r"(?:-|Economize\s+)(\d{2,3})%"
        r".{0,100}?"
        r"(R\$\s*[\d.,]+)",
        re.IGNORECASE,
    )

    for resultado in padrao.finditer(texto):
        nome = resultado.group(1).strip()
        desconto = int(resultado.group(2))
        preco = resultado.group(3).strip()

        if desconto <= 50:
            continue

        # Limpa textos que podem aparecer antes do nome
        nome = re.sub(r"\s+", " ", nome)

        # Evita resultados muito estranhos
        if len(nome) < 3:
            continue

        ofertas.append({
            "nome": nome,
            "desconto": desconto,
            "preco": preco,
        })

    # Remove duplicados
    unicas = {}
    for oferta in ofertas:
        chave = (
            oferta["nome"],
            oferta["desconto"],
            oferta["preco"],
        )
        unicas[chave] = oferta

    return list(unicas.values())


def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    resposta = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": mensagem,
            "disable_web_page_preview": True,
        },
        timeout=30,
    )

    print("Resposta do Telegram:")
    print(resposta.text)

    if not resposta.ok:
        raise Exception(
            f"Telegram rejeitou a mensagem: "
            f"{resposta.status_code} - {resposta.text}"
    )


def main():
    enviadas = carregar_enviadas()
    ofertas = buscar_ofertas()

    print(f"Ofertas encontradas: {len(ofertas)}")

    novas = []

    for oferta in ofertas:
        identificador = (
            f"{oferta['nome']}|"
            f"{oferta['desconto']}|"
            f"{oferta['preco']}"
        )

        if identificador not in enviadas:
            novas.append(oferta)
            enviadas.add(identificador)

    print(f"Ofertas novas: {len(novas)}")

    if novas:
        for oferta in novas:
            mensagem = (
                "🥳 NOVA OFERTA PS4\n\n"
                f"🧐 {oferta['nome']}\n"
                f"🤑 {oferta['desconto']}% OFF\n"
                f"🤓 {oferta['preco']}\n\n"
                "🙏🏼 PlayStation Store Brasil\n"
                f"{STORE_URL}"
            )

            enviar_telegram = ("https://api.telegram.org/bot"{BOT_TOKEN}/sendMessage=(mensagem) )

        salvar_enviadas(enviadas)

    else:
        print("Nenhuma oferta nova acima de 50%.")


if __name__ == "__main__":
    main()
