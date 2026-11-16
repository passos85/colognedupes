#!/usr/bin/env python3
"""Gera as páginas estáticas do CologneDupes a partir de data/perfumes.json e data/site.json.

Uso (na pasta do repositório):
    python3 tools/build.py            # usa o "url" de data/site.json
    python3 tools/build.py --url https://o-teu-utilizador.github.io/o-teu-repo

Não precisa de instalar nada (só Python 3).
"""
import json, sys, shutil, html, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data/perfumes.json").read_text(encoding="utf8"))
S = json.loads((ROOT / "data/site.json").read_text(encoding="utf8"))
if "--url" in sys.argv:
    S["url"] = sys.argv[sys.argv.index("--url") + 1]
URL = S["url"].rstrip("/")

F = {"doce": "Doces", "fresco": "Frescos", "especiado": "Especiados", "noite": "Noite",
     "trabalho": "Trabalho", "date": "Date", "dia": "Dia a dia"}
OC = {"noite": "Noite", "date": "Date", "festa": "Festa", "dia": "Dia a dia", "trabalho": "Trabalho"}
e = lambda s: html.escape(str(s), quote=True)
BYID = {p["id"]: p for p in D}
VERSION = datetime.date.today().isoformat()


def fraga(p):
    return "https://www.google.com/search?q=" + "site:fragrantica.com+" + (p["marca"] + " " + p["nome"]).replace(" ", "+").replace("&", "%26")


def page(depth, title, desc, path, body, extra_head="", noindex=False, root=None):
    r = root if root is not None else "../" * depth
    canon = f"{URL}/{path}"
    return f"""<!doctype html>
<html lang="pt-PT"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{'<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{e(canon)}">'}
<meta property="og:type" content="website"><meta property="og:locale" content="pt_PT">
<meta property="og:site_name" content="CologneDupes"><meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{e(canon)}">
<meta property="og:image" content="{URL}/assets/img/og.png"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0a0a0b">
<link rel="icon" href="{r}favicon.ico" sizes="any"><link rel="icon" type="image/png" href="{r}assets/img/icon-192.png">
<link rel="apple-touch-icon" href="{r}assets/img/apple-touch-icon.png">
<link rel="preload" href="{r}assets/fonts/montserrat-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}assets/style.css?v={VERSION}">
{extra_head}
</head><body data-root="{r}">
<a class="skip" href="#main">Saltar para o conteúdo</a>
<header><div class="w"><a class="logo" href="{r}">COLOGNEDUPES</a><nav aria-label="Principal"><a href="{r}">Início</a><a href="{r}perfumes/">Perfumes</a><a href="{r}comunidade/">Comunidade</a><a href="{e(S['tiktok']['perfil'])}" target="_blank" rel="noopener">TikTok</a></nav></div></header>
<main class="w" id="main">
{body}
</main>
<footer><div class="w"><p>Descrições, vibes e ocasiões são opinião do CologneDupes. As notas são indicativas e podem variar entre versões: consulta o Fragrantica e confirma antes de comprar.</p>
<p>Todas as marcas e nomes de produtos pertencem aos respetivos titulares. Este site é independente e não tem qualquer ligação às marcas mencionadas. Os perfumes aqui apresentados são fragrâncias próprias de cada marca, descritas pelas suas notas e ambiente.</p>
<p><a href="{r}privacidade/">Privacidade e aviso legal</a> · © CologneDupes</p></div></footer>
<script src="{r}assets/app.js?v={VERSION}" defer></script>
</body></html>"""


def card(p, r):
    notas = "".join(f'<span class="pill">{e(n)}</span>' for n in p["notas"][:3])
    tags = "".join(f'<span class="pill g">{F[t]}</span>' for t in [t for t in p["tags"] if t in F][:3])
    srch = e((p["marca"] + " " + p["nome"] + " " + " ".join(p["notas"]) + " " + " ".join(F[t] for t in p["tags"] if t in F)).lower())
    return f'<a class="card" href="{r}perfumes/{p["id"]}/" data-s="{srch}"><small>{e(p["marca"])}</small><h3>{e(p["nome"])}</h3><p class="np">{notas}</p><div>{tags}</div></a>'


def chips(cur, r):
    c = "".join(f'<a class="chip{" on" if cur == k else ""}" href="{r}vibe/{k}/">{v}</a>' for k, v in F.items())
    return f'<div class="chips"><a class="chip{" on" if cur is None else ""}" href="{r}perfumes/">Todos</a>{c}</div>'


def related(p):
    sc = []
    for q in D:
        if q["id"] == p["id"]:
            continue
        s = 2 * len(set(q["tags"]) & set(p["tags"])) + len(set(q["ocasioes"]) & set(p["ocasioes"])) + (1 if q["estacao"] == p["estacao"] else 0)
        sc.append((-s, q["id"], q))
    sc.sort(key=lambda x: (x[0], x[1]))
    return [x[2] for x in sc[:3]]


def giscus_block(term):
    g = S.get("giscus", {})
    if not (g.get("repo") and g.get("repoId") and g.get("categoriaId")):
        return '<p class="n">Os comentários vão abrir em breve.</p>'
    return (f'<div id="gc" data-repo="{e(g["repo"])}" data-repo-id="{e(g["repoId"])}" data-cat="{e(g.get("categoria","Comentarios"))}" '
            f'data-cat-id="{e(g["categoriaId"])}" data-term="{e(term)}"><button class="btn p" id="gcb" type="button">Mostrar comentários</button>'
            '<p class="n">Ao mostrar, carrega-se o Giscus (GitHub). É preciso conta GitHub para comentar. Vê a página de privacidade.</p></div>')


def write(rel, content):
    f = ROOT / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf8")


# limpar páginas geradas
for d in ("perfumes", "vibe", "comunidade", "privacidade"):
    shutil.rmtree(ROOT / d, ignore_errors=True)

T = S["tiktok"]
# ---------- início
feat = ["khamrah", "mandarin", "yara", "cdnim", "asad", "ana"]
home = f"""<div class="hero"><h1>Perfumes que cheiram a <em>luxo</em>,<br>sem custar uma fortuna</h1>
<p>Notas, vibe e ocasião de cada perfume, explicadas sem complicações. Descobre o teu antes de gastar dinheiro.</p>
<a class="btn p" href="perfumes/">Ver perfumes</a><a class="btn" href="{e(T['perfil'])}" target="_blank" rel="noopener">Seguir no TikTok</a></div>
<section><h2>Último TikTok</h2><div class="tt" id="tt" data-video="{e(T.get('video',''))}"><div><small>NOVO NO TIKTOK{(' · ' + e(T['data'])) if T.get('data') else ''}</small><h3>{e(T['titulo'])}</h3><p>@colognedupes.pt</p></div>
<div class="act">{'<button class="btn" id="ttb" type="button">Ver aqui</button>' if T.get('video') else ''}<a class="btn p" href="{e(T.get('video') or T['perfil'])}" target="_blank" rel="noopener">Abrir no TikTok</a></div></div></section>
<section><h2>Perfume do dia</h2><div id="pdd" class="grid one"></div></section>
<section><h2>Descobre o teu perfume</h2><p class="n lead">Três perguntas rápidas. Nada é guardado.</p><div id="quiz" class="quiz"></div></section>
<section><h2>Explora por vibe</h2>{chips('', '')}</section>
<section><h2>Em destaque</h2><div class="grid">{''.join(card(BYID[i], '') for i in feat)}</div></section>
<section><h2>Comunidade</h2><p class="lead">Dúvidas, recomendações e descobertas de quem gosta de perfumes em Portugal.</p><a class="btn p" href="comunidade/">Entrar na comunidade</a></section>"""
write("index.html", page(0, "CologneDupes: perfumes acessíveis explicados", "Notas, vibe e ocasião de perfumes acessíveis, explicadas sem complicações. Segue @colognedupes.pt no TikTok.", "", home))

# ---------- listagem
body = f"""<section><h1 class="h2">Todos os perfumes</h1>{chips(None, '../')}
<label class="sr" for="q">Pesquisar</label><input id="q" type="search" placeholder="Pesquisar por nome, marca ou nota…" autocomplete="off">
<p class="n" id="qn">{len(D)} perfumes</p>
<div class="grid" id="lista">{''.join(card(p, '../') for p in D)}</div></section>"""
write("perfumes/index.html", page(1, "Todos os perfumes | CologneDupes", f"{len(D)} perfumes acessíveis com notas, vibe e ocasião explicadas.", "perfumes/", body))

# ---------- filtros
for k, v in F.items():
    L = [p for p in D if k in p["tags"]]
    body = f"""<section><h1 class="h2">Perfumes {v.lower()}</h1>{chips(k, '../../')}<p class="n">{len(L)} perfumes</p>
<div class="grid">{''.join(card(p, '../../') for p in L)}</div></section>"""
    write(f"vibe/{k}/index.html", page(2, f"Perfumes {v.lower()} | CologneDupes", f"{len(L)} perfumes na categoria {v.lower()}, com notas e ocasião.", f"vibe/{k}/", body))

# ---------- perfumes
for p in D:
    py = ""
    if p.get("piramide"):
        nm = {"topo": "Topo", "coracao": "Coração", "base": "Base"}
        py = "<h3>Pirâmide olfativa</h3>" + "".join(f'<p class="py"><b>{nm[k]}:</b> {e(" · ".join(v))}</p>' for k, v in p["piramide"].items())
    vibe = "".join(f'<span class="pill">{F[t]}</span>' for t in p["tags"] if t in ("doce", "fresco", "especiado")) or '<span class="pill">Versátil</span>'
    aviso = "Notas aproximadas: confirma no Fragrantica antes de comprar." if not p.get("verificado", True) else "Notas principais indicativas: confirma a pirâmide e as opiniões no Fragrantica."
    rel = "".join(card(q, "../../") for q in related(p))
    body = f"""<article class="det"><a class="back" href="../">Voltar aos perfumes</a><div class="m">{e(p['marca'])}</div><h1>{e(p['nome'])}</h1>
<p>{e(p['descricao'])}</p><h3>Notas principais</h3><div>{''.join(f'<span class="pill g">{e(n)}</span>' for n in p['notas'])}</div>{py}
<p class="mt"><a class="btn" href="{e(fraga(p))}" target="_blank" rel="noopener">Ficha completa no Fragrantica</a></p><p class="n">{aviso}</p>
<h3>Vibe</h3><div>{vibe}</div><h3>Ocasiões</h3><div>{''.join(f'<span class="pill">{OC.get(o, o)}</span>' for o in p['ocasioes'])}</div>
<h3>Melhor altura do ano</h3><p>{e(p['estacao'][0].upper() + p['estacao'][1:])}.</p></article>
<section><h2>Comentários</h2>{giscus_block('perfume-' + p['id'])}</section>
<section><h2>Também podes gostar</h2><div class="grid">{rel}</div></section>"""
    ttl = f"{p['nome']} ({p['marca'].title()}): notas, vibe e ocasião | CologneDupes"
    write(f"perfumes/{p['id']}/index.html", page(2, ttl, p["descricao"][:155], f"perfumes/{p['id']}/", body))

# ---------- comunidade
body = f"""<section><h1 class="h2">Comunidade</h1><p class="lead">Conversa sobre perfumes em Portugal: dúvidas, recomendações, comparações e descobertas. Respeita as outras pessoas e não partilhes dados pessoais.</p>
{giscus_block('comunidade')}</section>"""
write("comunidade/index.html", page(1, "Comunidade | CologneDupes", "Fórum para quem gosta de perfumes em Portugal.", "comunidade/", body))

# ---------- privacidade
contacto = f'Contacto: <a href="mailto:{e(S["contacto"])}">{e(S["contacto"])}</a>.' if S.get("contacto") else "Contacto: através do perfil @colognedupes.pt no TikTok."
body = f"""<section class="det"><h1>Privacidade e aviso legal</h1>
<h3>O que este site recolhe</h3><p>Este site não usa cookies, não tem contas e não recolhe dados pessoais nem estatísticas de visitas. O teste &ldquo;Descobre o teu perfume&rdquo; corre no teu navegador e não guarda nada.</p>
<h3>Alojamento</h3><p>O site está alojado no GitHub Pages (GitHub, Inc.). O alojamento pode registar dados técnicos de ligação, como o endereço IP, para funcionamento e segurança. Consulta a declaração de privacidade do GitHub.</p>
<h3>Serviços de terceiros (só carregam se clicares)</h3><p><b>TikTok:</b> o vídeo incorporado só é carregado se carregares em &ldquo;Ver aqui&rdquo;. Ao fazê-lo, o TikTok pode colocar cookies e tratar dados segundo a sua política.</p>
<p><b>Comentários (Giscus / GitHub Discussions):</b> só carregam se carregares em &ldquo;Mostrar comentários&rdquo;. Para comentar é necessária uma conta GitHub e o comentário fica público, sob a política do GitHub. Podes pedir a remoção de um comentário teu.</p>
<p><b>Fragrantica:</b> os botões abrem uma pesquisa externa; não partilhamos nada com esse site.</p>
<h3>Comunidade</h3><p>Os comentários são da responsabilidade de quem os publica e podem ser moderados ou removidos, em especial se forem ofensivos, enganosos ou incluírem dados pessoais.</p>
<h3>Marcas e conteúdo</h3><p>Todas as marcas e nomes de produtos pertencem aos respetivos titulares. Este site é independente e não tem ligação, afiliação ou patrocínio de qualquer marca mencionada. As descrições são opinião editorial e as notas são indicativas. Confirma sempre a composição, as embalagens e as informações do vendedor antes de comprar.</p>
<h3>Contacto</h3><p>{contacto}</p></section>"""
write("privacidade/index.html", page(1, "Privacidade e aviso legal | CologneDupes", "Como este site trata dados e informações legais.", "privacidade/", body))

# ---------- 404
write("404.html", page(0, "Página não encontrada | CologneDupes", "Página não encontrada.", "404.html",
      f'<section class="hero"><h1>Esta página <em>não existe</em></h1><p>Pode ter mudado de sítio.</p><a class="btn p" href="{URL}/">Ir para o início</a> <a class="btn" href="{URL}/perfumes/">Ver perfumes</a></section>', noindex=True, root=URL + "/"))

# ---------- robots + sitemap
urls = ["", "perfumes/", "comunidade/", "privacidade/"] + [f"vibe/{k}/" for k in F] + [f"perfumes/{p['id']}/" for p in D]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"<url><loc>{URL}/{u}</loc><lastmod>{VERSION}</lastmod></url>\n" for u in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {URL}/sitemap.xml\n")
print("ok:", len(urls), "páginas;", URL)
