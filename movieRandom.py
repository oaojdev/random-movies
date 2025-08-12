from flask import Flask, render_template_string, send_from_directory
import requests
import os
import random

app = Flask(__name__)

# Sua chave da API TMDb
API_KEY = "a7ab3cc92f4a8a884adb8f7b5f953e78"
BASE_URL = "https://api.themoviedb.org/3"

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, ""),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

def get_max_id():
    """Obtém o ID mais alto de filme registrado na TMDb."""
    url = f"{BASE_URL}/movie/latest?api_key={API_KEY}&language=pt-BR"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json().get("id", 100000)  # fallback se não vier id

def get_movie_by_id(movie_id):
    """Busca filme pelo ID."""
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=pt-BR"
    return requests.get(url)

@app.route("/")
def random_movie():
    try:
        max_id = get_max_id()

        while True:
            random_id = random.randint(1, max_id)
            resp = get_movie_by_id(random_id)

            if resp.status_code == 200:
                data = resp.json()
                if not data.get("title"):  # ignora se não tiver título
                    continue

                genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "Não informado"

                return render_template_string("""
                    <link rel="icon" href="/favicon.ico" type="image/x-icon">
                    <h1>🎬 Filme Aleatório</h1>
                    <p><b>{{ title }}</b> ({{ year }})</p>
                    <p><b>Gênero:</b> {{ genres }}</p>
                    <p><b>Nota Média:</b> {{ vote_average }}</p>
                    <p><b>Sinopse:</b> {{ overview }}</p>
                """,
                title=data["title"],
                year=data.get("release_date", "")[:4],
                genres=genres,
                vote_average=data.get("vote_average", "N/A"),
                overview=data.get("overview", "Sem sinopse disponível"))

            elif resp.status_code == 404:
                continue  # tenta outro ID
            else:
                return f"<p>❌ Erro ao buscar filme. Status: {resp.status_code}</p>"

    except Exception as e:
        return f"<p>⚠ Erro: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
