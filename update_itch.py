"""Actualiza la sección de juegos de itch.io en el README del perfil de GitHub."""
import html
import json
import os
import re
import urllib.request

API_KEY = os.environ["ITCH_API_KEY"]
COLUMNS = 3          # tarjetas por fila
README = "README.md"
START, END = "<!-- ITCH:START -->", "<!-- ITCH:END -->"


def fetch_games():
    url = f"https://itch.io/api/1/{API_KEY}/my-games"
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.load(r)
    games = [g for g in data.get("games", []) if g.get("published")]
    games.sort(key=lambda g: g.get("published_at", ""), reverse=True)
    return games


def card(g):
    title = html.escape(g["title"])
    desc = html.escape(g.get("short_text") or "")
    cover = g.get("cover_url")
    img = (
        f'<img src="{cover}" width="315" height="250" alt="{title}">'
        if cover else ""
    )
    return (
        f'<td align="center" width="{100 // COLUMNS}%" valign="top">'
        f'<a href="{g["url"]}">{img}<br><b>{title}</b></a><br>'
        f"<sub>{desc}</sub></td>"
    )


def build_table(games):
    rows = []
    for i in range(0, len(games), COLUMNS):
        cells = "".join(card(g) for g in games[i:i + COLUMNS])
        rows.append(f"<tr>{cells}</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def main():
    games = fetch_games()
    block = f"{START}\n{build_table(games)}\n{END}"
    with open(README, encoding="utf-8") as f:
        text = f.read()
    pattern = re.compile(f"{re.escape(START)}.*?{re.escape(END)}", re.S)
    if not pattern.search(text):
        raise SystemExit("No encuentro los marcadores ITCH:START / ITCH:END en el README")
    new_text = pattern.sub(lambda _: block, text)
    if new_text != text:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_text)


if __name__ == "__main__":
    main()
