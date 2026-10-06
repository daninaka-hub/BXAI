#!/usr/bin/env python3
"""Utilitários do squad BXAI: lê briefings aprovados, valida texto e gera a página de validação."""
import sys, re, json, html, unicodedata, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]  # agente-conteudo
CONT = ROOT / "conteudo"
PAGINA = ROOT / "validacao" / "artigos.html"
STATUS = ROOT / "status"
GITHUB = "https://github.com/daninaka-hub/BXAI/blob/main/agente-conteudo/"
AGENTES = {
    "pesquisador": ("Pesquisador", "todo dia às 7h"),
    "head": ("Head de Conteúdo", "segundas às 8h"),
    "copywriter": ("Copywriter", "a cada 30 min, só quando há briefing aprovado"),
}

def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]

def tabela(path):
    out = []
    for ln in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if ln.startswith("|") and not ln.startswith("|---") and not ln.startswith("| Semana") and not ln.startswith("| Código"):
            out.append((ln, _cells(ln)))
    return out

def slugify(s, n=7):
    s = re.sub(r"\(.*?\)", "", s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    w = re.findall(r"[a-z0-9]+", s.lower())
    stop = {"de", "do", "da", "a", "o", "e", "que", "um", "uma", "para", "por", "com", "em", "os", "as"}
    w = [x for x in w if x not in stop][:n]
    return "-".join(w)

def indice():
    return tabela(CONT / "indice-artigos.md")

def proximo_codigo():
    nums = [int(m.group(1)) for _, c in indice() if (m := re.match(r"Artigo (\d+)", c[0]))]
    return (max(nums) if nums else 0) + 1

def listar():
    linhas = tabela(CONT / "decisoes-pauta.md")
    if not linhas:
        return []
    semana = max(c[0] for _, c in linhas)
    sel = [(ln, c) for ln, c in linhas if c[0] == semana and c[-1] == "Sim"]
    n = proximo_codigo()
    briefs = []
    for i, (ln, c) in enumerate(sel):
        briefs.append({"codigo": n + i, "slug": slugify(c[3]), "pilar": c[2], "teoria": c[3], "apoio": c[4], "tese": (c[5] if len(c) > 6 and c[5].lower() != "a definir" else ""), "linha": ln})
    return briefs

def marcar(linha, texto):
    p = CONT / "decisoes-pauta.md"
    t = p.read_text(encoding="utf-8")
    assert linha in t, "linha do briefing não encontrada"
    nova = linha.rstrip()
    assert nova.endswith("| Sim |")
    nova = nova[: -len("| Sim |")] + f"| {texto} |"
    p.write_text(t.replace(linha, nova, 1), encoding="utf-8")

def indexar(codigo, slug, titulo, pilar, teoria, apoio):
    p = CONT / "indice-artigos.md"
    t = p.read_text(encoding="utf-8").rstrip("\n")
    t += f"\n| Artigo {codigo} | {titulo} | {pilar} | {teoria} | {apoio} | Em validação | conteudo/artigos/{slug}.md |\n"
    p.write_text(t, encoding="utf-8")

def titulo_do_artigo(slug):
    primeira = (CONT / "artigos" / f"{slug}.md").read_text(encoding="utf-8").splitlines()[0]
    return primeira.lstrip("# ").strip()

def caminhos(slug):
    return [CONT / "artigos" / f"{slug}.md", CONT / "posts-linkedin" / f"{slug}.md", CONT / "roteiros-video" / f"{slug}.md"]

SIGLAS_OK = {"EUA", "IA", "PIB", "CEO", "CFO", "SaaS", "ERP"}

PROMESSAS_PROIBIDAS = [
    (r"hist[óo]rico de (?:altera|mudan|valor)|toda altera[çc][ãa]o de valor|every (?:value )?change .{0,20}(?:is )?(?:recorded|logged)|historial de (?:cambios|valores)", "histórico de alteração de valor (P02, não existe)"),
    (r"notifica|menciona(?:r|ndo)? (?:um|o) respons|menção a respons|notif(?:y|ies|ication)|mention(?:s)? (?:an|the) owner|notifica(?:r|ción)", "notificação ou menção a responsável (P05, não existe)"),
    (r"propag|todos os or[çc]amentos (?:que a usam )?mudam|recalcula(?:m)? (?:sozinh|automatic)|all (?:the )?budgets (?:that use it )?(?:update|change)|se actualizan? (?:solos|autom)", "propagação automática da premissa (P12, pendente)"),
    (r"fluxo de aprova|aprova[çc][ãa]o formal|envia o or[çc]amento e o gestor aprova|approval workflow|flujo de aprobaci", "fluxo de aprovação (P21, pendente)"),
    (r"(?:IA|agente) pede (?:sua )?confirma|confirma[çc][ãa]o antes de executar|asks? for (?:your )?confirmation before|pide (?:tu )?confirmaci", "IA que pede confirmação antes de alterar (P33, não existe)"),
    (r"compara(?:r|ção)? .{0,30}planejado .{0,30}realizado|planned .{0,20}(?:vs|against|with) .{0,10}actual", "comparação automática planejado x realizado (P42, a classificar)"),
    (r"erp (?:atualiza|alimenta)|integra[çc][ãa]o com (?:o )?erp|erp (?:updates|feeds)|el erp (?:actualiza|alimenta)", "integração com ERP (P13 e P29, não existe ou com contorno)"),
    (r"importa(?:r|[çc][ãa]o)? (?:d[ao] )?(?:sua )?planilha|importa(?:r)? (?:o seu )?excel|import (?:your )?(?:spreadsheet|excel)|importar (?:tu )?(?:planilla|excel)", "importação de planilha (P28, não existe)"),
    (r"de-para|mapeamento entre planos de contas|chart[- ]of[- ]accounts mapping|mapeo entre planes de cuentas", "de-para entre planos de contas (P24, não existe)"),
    (r"simula(?:r|ção|ções)? (?:um )?cen[áa]rio|compara(?:r)? dois caminhos|simulate (?:a )?scenario|simular (?:un )?escenario", "cenários e simulações (P48, P49, P52, a classificar)"),
    (r"intragrupo|elimina(?:r|ção)? .{0,20}transa[çc][õo]es entre|multimoeda|multi-?currency|m[úu]ltiplas moedas|mais de uma moeda", "consolidação intragrupo ou multimoeda (P25, P37, não existe)"),
    (r"nenhum dado .{0,30}treina|dados .{0,20}n[ãa]o treinam|data .{0,20}(?:does not|doesn't|never) train", "dados não treinam modelo de terceiros (P36, pendente)"),
    (r"reduz(?:ir|iria)? (?:o )?custo|economiz|corta(?:r)? (?:o )?custo|elimina(?:r)? (?:um |o )?(?:FTE|analista)|cut(?:s|ting)? costs?|saves? (?:time|money)", "ganho de custo ou FTE (não permitido)"),
]

def _fechamentos(texto):
    """Devolve os trechos do artigo que citam a BudgetXpert: o parágrafo e o subtítulo do fechamento, e as linhas do post."""
    achados = []
    for m in re.finditer(r"(?:^|\n)(## [^\n]+\n+(?:(?!\n## |\n(?:Fonte|Fontes|Source|Sources|Fuente|Fuentes):)[\s\S])*?budgetxpert\.ai[^\n]*)", texto):
        achados.append(m.group(1))
    if not achados:
        achados = [x for x in texto.splitlines() if "budgetxpert" in x.lower()]
    return achados

LINK_SITE = "[budgetxpert.ai](https://www.budgetxpert.ai)"

def _lint_link_site(texto, nome, md):
    """Todo budgetxpert.ai do artigo é link para https://www.budgetxpert.ai. No post, o endereço é www.budgetxpert.ai."""
    if md:
        sobra = texto.replace(LINK_SITE, "")
        if re.search(r"budgetxpert\.ai", sobra, flags=re.I):
            return [f"{nome}: todo \"budgetxpert.ai\" precisa ser link, no formato {LINK_SITE}"]
        return []
    sobra = re.sub(r"www\.budgetxpert\.ai", "", texto, flags=re.I)
    if re.search(r"budgetxpert\.ai", sobra, flags=re.I):
        return [f"{nome}: no post, escrever www.budgetxpert.ai"]
    return []

def lint_promessas(slug):
    erros = []
    art, post, rot = caminhos(slug)
    fontes = []
    for arq in (art, post):
        if arq.exists():
            fontes.append((arq.parent.name + "/" + arq.name, arq.read_text(encoding="utf-8")))
    d = ler_idiomas(slug) if (IDIOMAS / f"{slug}.json").exists() else None
    if d:
        for lg in ("en", "es"):
            for campo in ("artigo", "post"):
                fontes.append((f"idiomas {lg}.{campo}", str(d.get(lg, {}).get(campo, ""))))
    for nome, tx in fontes:
        for trecho in _fechamentos(tx):
            for padrao, rotulo in PROMESSAS_PROIBIDAS:
                m = re.search(padrao, trecho, flags=re.I)
                if m:
                    erros.append(f"{nome}: promessa proibida no fechamento com a BudgetXpert, {rotulo}, perto de \"{trecho[max(0, m.start()-25):m.end()+25].strip()}\"")
    return erros

def _lint_subtitulo(texto, nome, com_titulo):
    """O artigo tem um subtítulo (### Prefixo: frase, até 100 caracteres) logo depois do título."""
    if com_titulo:
        texto = re.sub(r"^#\s.*\n", "", texto, count=1)
    prim = texto.strip().split("\n\n")[0].strip()
    if not prim.startswith("### "):
        return [f"{nome}: falta o subtítulo com \"### \" logo depois do título (formato \"Prefixo: frase\")"]
    sub = prim[4:].strip()
    erros = []
    if ":" not in sub:
        erros.append(f"{nome}: o subtítulo precisa do formato \"Prefixo: frase\"")
    if len(sub) > 100:
        erros.append(f"{nome}: subtítulo com {len(sub)} caracteres, o limite é 100")
    return erros

def lint(slug):
    """Devolve a lista de problemas encontrados nos três arquivos."""
    erros = []
    art, post, rot = caminhos(slug)
    arte = CONT / "artes" / f"{slug}.md"
    for p in (art, post, rot, arte):
        if not p.exists() or not p.read_text(encoding="utf-8").strip():
            erros.append(f"{p.name}: arquivo ausente ou vazio ({p.parent.name})")
            continue
        t = p.read_text(encoding="utf-8")
        for m in re.finditer(r"[\u2014\u2013]", t):
            erros.append(f"{p.parent.name}/{p.name}: travessão perto de \"{t[max(0, m.start()-30):m.start()+30].strip()}\"")
        for m in re.finditer(r",\s+e\s", t):
            erros.append(f"{p.parent.name}/{p.name}: vírgula seguida de \"e\" perto de \"{t[max(0, m.start()-30):m.start()+30].strip()}\"")
    # contexto para leitor que não conhece o assunto
    for arq in (art, post, rot):
        if not arq.exists():
            continue
        t = arq.read_text(encoding="utf-8").split("\nFonte:")[0]
        vistas = set()
        for m in re.finditer(r"(?<![#\w])[A-Z]{2,6}(?:&[A-Z])?\b(?!\$)", t):
            sg = m.group(0)
            if sg in vistas or sg in SIGLAS_OK:
                continue
            vistas.add(sg)
            depois = t[m.end():m.end() + 3]
            antes = t[max(0, m.start() - 2):m.start()]
            if not (depois.lstrip().startswith(("(", ",")) or antes.endswith("(")):
                erros.append(f"aviso: {arq.parent.name}/{arq.name}: sigla {sg} sem explicação na primeira menção")
    if art.exists():
        paras = [x for x in art.read_text(encoding="utf-8").split("\n\n") if x.strip() and not x.startswith("#")]
        if paras and re.match(r"(Esse|Essa|Esses|Essas|Isso|Aquele|Aquela|Ele|Ela|Eles|Elas)\b", paras[0].strip()):
            erros.append("artigo: a primeira frase começa com pronome ou demonstrativo, sem apresentar o assunto antes")
    if art.exists():
        corpo = re.sub(r"^#.*\n", "", art.read_text(encoding="utf-8"))
        corpo = corpo.split("\nFonte:")[0]
        palavras = len(corpo.split())
        if palavras < 800 or palavras > 1600:
            erros.append(f"artigo com {palavras} palavras, a meta é cerca de 1000 (aceito de 800 a 1600)")
    if post.exists():
        linhas = post.read_text(encoding="utf-8").splitlines()
        if len(linhas) < 5 or [x.strip() for x in linhas[1:5]] != ["."] * 4:
            erros.append("post: depois do header precisam vir quatro linhas só com um ponto final")
    erros += lint_idiomas(slug)
    erros += lint_promessas(slug)
    if art.exists():
        erros += _lint_link_site(art.read_text(encoding="utf-8"), "artigo", True)
    if post.exists():
        erros += _lint_link_site(post.read_text(encoding="utf-8"), "post", False)
    _d = ler_idiomas(slug) if (IDIOMAS / f"{slug}.json").exists() else None
    for lg in ("en", "es"):
        if _d:
            erros += _lint_link_site(str(_d.get(lg, {}).get("artigo", "")), f"idiomas {lg}.artigo", True)
            erros += _lint_link_site(str(_d.get(lg, {}).get("post", "")), f"idiomas {lg}.post", False)
    if art.exists():
        erros += _lint_subtitulo(art.read_text(encoding="utf-8"), "artigo", True)
    if (IDIOMAS / f"{slug}.json").exists():
        di = ler_idiomas(slug) or {}
        for lg in ("en", "es"):
            erros += _lint_subtitulo(str(di.get(lg, {}).get("artigo", "")), f"idiomas {lg}.artigo", False)
    if art.exists() and "budgetxpert.ai" not in art.read_text(encoding="utf-8").lower():
        erros.append("artigo: falta o fechamento com a BudgetXpert e o link budgetxpert.ai (Passo 1.5)")
    if post.exists() and "budgetxpert.ai" not in post.read_text(encoding="utf-8").lower():
        erros.append("post: falta a frase com a BudgetXpert e o link budgetxpert.ai")
    d_ = ler_idiomas(slug) if (IDIOMAS / f"{slug}.json").exists() else None
    if d_:
        for lg in ("en", "es"):
            for campo in ("artigo", "post"):
                if "budgetxpert.ai" not in str(d_.get(lg, {}).get(campo, "")).lower():
                    erros.append(f"idiomas: {lg}.{campo} sem o link budgetxpert.ai")
    for arq in (art, post, rot, IDIOMAS / f"{slug}.json"):
        if arq.exists():
            tx = arq.read_text(encoding="utf-8")
            for m in re.finditer(r"não se aplica|nao se aplica|onde não vale|pode seguir sem|não vale a pena|dispensa (?:o|a) (?:dono|critério|revisão)|does not apply|can go without|no se aplica|puede seguir sin|mais devagar|mais lent[oa]|atrasa o (?:fechamento|ciclo)|custo de governar|tem uma ressalva|100% governad|slower|slows? (?:down )?the|más lent[oa]|más despacio|más tarde en cerrar", tx, flags=re.I):
                erros.append(f"{arq.parent.name}/{arq.name}: trecho enfraquece a governança (\"{tx[max(0, m.start()-30):m.end()+30].strip()}\")")
    return erros

IDIOMAS = CONT / "idiomas"
JSONS = CONT / "json"
SEO_CAMPOS = ("palavra_chave", "palavras_secundarias", "titulo_seo", "meta_descricao", "slug_url", "excerpt", "neste_artigo", "resumo_geo", "faq", "entidades")
NOMES_IDIOMA = {"pt": "Português", "en": "English", "es": "Español"}

def ler_idiomas(slug):
    p = IDIOMAS / f"{slug}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

def _primeiras_palavras(texto, n=100):
    return " ".join(re.sub(r"[#*_>\[\]]", " ", texto).split()[:n]).lower()

def lint_idiomas(slug):
    """Confere o arquivo de idiomas (en, es) e o bloco de SEO e GEO dos três idiomas."""
    p = IDIOMAS / f"{slug}.json"
    if not p.exists():
        return [f"idiomas/{p.name}: arquivo ausente"]
    cru = p.read_text(encoding="utf-8")
    if re.search(r"[\u2014\u2013]|\\u201[34]", cru):
        return [f"idiomas/{p.name}: travessão no texto"]
    try:
        d = json.loads(cru)
    except Exception as e:
        return [f"idiomas/{p.name}: JSON inválido ({e})"]
    erros = []
    for lg in ("pt", "en", "es"):
        b = d.get(lg)
        if not isinstance(b, dict):
            erros.append(f"idiomas/{p.name}: falta o bloco {lg}")
            continue
        if lg != "pt":
            for c in ("titulo", "artigo", "post", "roteiro"):
                if not str(b.get(c, "")).strip():
                    erros.append(f"idiomas/{p.name}: {lg}.{c} ausente ou vazio")
        seo = b.get("seo")
        if not isinstance(seo, dict):
            erros.append(f"idiomas/{p.name}: {lg}.seo ausente")
            continue
        faltam = [c for c in SEO_CAMPOS if not seo.get(c)]
        if faltam:
            erros.append(f"idiomas/{p.name}: {lg}.seo sem {', '.join(faltam)}")
            continue
        if len(seo["titulo_seo"]) > 60:
            erros.append(f"idiomas/{p.name}: {lg}.seo.titulo_seo com {len(seo['titulo_seo'])} caracteres, o limite é 60")
        if len(seo["meta_descricao"]) > 155:
            erros.append(f"idiomas/{p.name}: {lg}.seo.meta_descricao com {len(seo['meta_descricao'])} caracteres, o limite é 155")
        faq = seo["faq"]
        if not isinstance(faq, list) or len(faq) < 3 or any(not (isinstance(x, dict) and x.get("pergunta") and x.get("resposta")) for x in faq):
            erros.append(f"idiomas/{p.name}: {lg}.seo.faq precisa de 3 perguntas, cada uma com resposta")
        kw = str(seo["palavra_chave"]).lower()
        if kw not in seo["titulo_seo"].lower():
            erros.append(f"aviso: idiomas/{p.name}: {lg}.seo.titulo_seo não contém a palavra-chave")
        if lg == "pt":
            art = caminhos(slug)[0]
            corpo = art.read_text(encoding="utf-8") if art.exists() else ""
            primeiras = _primeiras_palavras(corpo)
        else:
            primeiras = _primeiras_palavras(str(b.get("artigo", "")))
            n = len(str(b.get("artigo", "")).split("\nFonte:")[0].split()) if lg != "pt" else 0
            if lg != "pt" and (n < 700 or n > 1600):
                erros.append(f"aviso: idiomas/{p.name}: {lg}.artigo com {n} palavras (esperado de 700 a 1600)")
        if kw not in primeiras:
            erros.append(f"aviso: idiomas/{p.name}: {lg}, a palavra-chave não aparece nas primeiras 100 palavras do artigo")
    return erros

def _sem_pontos(texto):
    return "\n".join(x for x in texto.splitlines() if x.strip() != ".").strip()

CATEGORIAS = {"controllership": "controllership", "finance automation": "finance-automation", "forecasting methods": "forecasting",
              "strategic planning": "strategic-planning", "integrated planning": "integrated-planning", "fp&a fundamentals": "fpa-fundamentals",
              "leadership roles": "leadership", "organization": "organization"}
AUTOR = {"name": "Daniel Nakamura", "avatar": "/blog-media/autor-daniel-nakamura.webp"}
TITULO_NESTE = {"pt": "Neste artigo", "en": "In this article", "es": "En este artículo"}
SUFIXO = {"pt": "br", "en": "en", "es": "es"}

def _inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)

def _links_html(h):
    """Depois de esc(): transforma [texto](url) e o endereço do post em links clicáveis."""
    h = re.sub(r"\[(.+?)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', h)
    return re.sub(r'(?<![">/\w.])(www\.budgetxpert\.ai)', r'<a href="https://\1" target="_blank" rel="noopener">\1</a>', h)

def md_para_blocos(corpo, lg, neste):
    """Converte o markdown do artigo nos blocos de conteúdo do blog."""
    out, intro = [], True
    for b in re.split(r"\n\s*\n", corpo.strip()):
        b = b.strip()
        if not b:
            continue
        linhas = b.splitlines()
        if b.startswith("### "):
            out.append({"type": "heading", "level": 3, "content": b[4:].strip()})
        elif b.startswith("## "):
            out.append({"type": "heading", "level": 2, "content": b[3:].strip()})
        elif all(re.match(r"[-*] ", x) for x in linhas):
            out.append({"type": "list", "ordered": False, "items": [_inline(x[2:].strip()) for x in linhas]})
        elif all(re.match(r"\d+\. ", x) for x in linhas):
            out.append({"type": "list", "ordered": True, "items": [_inline(re.sub(r"^\d+\.\s*", "", x)) for x in linhas]})
        elif all(x.startswith("|") for x in linhas):
            linhas = [x for x in linhas if not re.match(r"\|\s*:?-+", x)]
            cel = [[_inline(c.strip()) for c in x.strip().strip("|").split("|")] for x in linhas]
            out.append({"type": "table", "headers": cel[0], "rows": cel[1:]})
        elif re.match(r"(Fonte|Fontes|Source|Sources|Fuente|Fuentes):", b):
            out.append({"type": "divider"})
            out.append({"type": "paragraph", "content": " ".join(b.split())})
        else:
            out.append({"type": "paragraph", "content": _inline(" ".join(b.split()))})
            if intro:
                out.append({"type": "callout", "variant": "blue", "icon": "\U0001F4CC", "title": TITULO_NESTE[lg], "content": neste})
                intro = False
    return out

def montar_json(slug):
    """Monta um JSON por idioma (br, en, es) no formato do blog. O português vem dos .md, en e es do arquivo de idiomas."""
    d = ler_idiomas(slug)
    if not d:
        return None
    art = caminhos(slug)[0]
    t = art.read_text(encoding="utf-8")
    titulos = {"pt": re.match(r"#\s*(.+)", t).group(1).strip(), "en": d.get("en", {}).get("titulo", ""), "es": d.get("es", {}).get("titulo", "")}
    corpos = {"pt": re.sub(r"^#.*\n", "", t, count=1).strip(), "en": d.get("en", {}).get("artigo", ""), "es": d.get("es", {}).get("artigo", "")}
    codigo, pilar = "", ""
    for _, c in indice():
        if pathlib.Path(c[6]).stem == slug:
            codigo, pilar = c[0], c[2]
    n = int(re.search(r"\d+", codigo).group()) if codigo else 0
    if not d.get("data"):
        d["data"] = _agora().strftime("%Y-%m-%d")
        (IDIOMAS / f"{slug}.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    primeiro = re.split(r"\s*/\s*", pilar.strip().lower())[0]
    categoria = CATEGORIAS.get(primeiro, slugify(primeiro, 3))
    base = d["pt"]["seo"]["slug_url"]
    JSONS.mkdir(exist_ok=True)
    for velho in JSONS.glob(f"{slug}*.json"):
        velho.unlink()
    saidas = {}
    for lg in ("pt", "en", "es"):
        seo = d[lg]["seo"]
        chaves = [seo["palavra_chave"]] + list(seo["palavras_secundarias"])
        palavras = len(re.sub(r"[#*]", " ", corpos[lg]).split())
        doc = {
            "seo": {"title": seo["titulo_seo"], "description": seo["meta_descricao"], "keywords": chaves},
            "id": str(15 + n),
            "slug": seo["slug_url"],
            "title": titulos[lg],
            "excerpt": seo["excerpt"],
            "coverImage": f"/blog-media/{base}-capa.webp",
            "date": d["data"],
            "author": AUTOR,
            "category": categoria,
            "tags": chaves[:5],
            "templateType": "guide",
            "readingTime": f"{max(1, -(-palavras // 200))} min",
            "featured": False,
            "content": md_para_blocos(corpos[lg], lg, seo["neste_artigo"]),
        }
        dest = JSONS / f"{base}-{SUFIXO[lg]}.json"
        dest.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        saidas[lg] = dest
    return saidas

PREVISAO_MIN = {"pesquisador": 20, "head": 10, "copywriter": 15}

def _agora():
    return datetime.datetime.now().astimezone()

def iniciar_status(agente, resumo, previsao_min=None):
    STATUS.mkdir(exist_ok=True)
    ant = ler_status(agente) or {}
    dur = ant.get("duracoes", [])
    prev = previsao_min or (round(sum(dur[-3:]) / len(dur[-3:])) if dur else PREVISAO_MIN.get(agente, 15))
    ini = _agora()
    d = {"agente": agente, "resultado": "executando", "resumo": resumo, "commit": "", "inicio": ini.isoformat(timespec="minutes"),
         "previsao": (ini + datetime.timedelta(minutes=prev)).isoformat(timespec="minutes"), "duracoes": dur,
         "anterior": {k: ant.get(k, "") for k in ("resultado", "quando", "resumo", "commit")} if ant.get("resultado") != "executando" else ant.get("anterior", {})}
    (STATUS / f"{agente}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

def gravar_status(agente, resultado, resumo, commit="", quando=None):
    STATUS.mkdir(exist_ok=True)
    ant = ler_status(agente) or {}
    agora = quando or _agora().isoformat(timespec="minutes")
    dur = list(ant.get("duracoes", []))
    d = {"agente": agente, "resultado": resultado, "quando": agora, "resumo": resumo, "commit": commit}
    if ant.get("inicio") and not quando:
        ini = datetime.datetime.fromisoformat(ant["inicio"])
        minutos = max(1, round((datetime.datetime.fromisoformat(agora) - ini).total_seconds() / 60))
        d["inicio"] = ant["inicio"]
        d["duracao_min"] = minutos
        if resultado == "ok":
            dur.append(minutos)
    d["duracoes"] = dur[-5:]
    (STATUS / f"{agente}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

def proxima_execucao(agente):
    agora = _agora()
    if agente == "pesquisador":
        n = agora.replace(hour=7, minute=0, second=0, microsecond=0)
        if n <= agora:
            n += datetime.timedelta(days=1)
        return n.strftime("%d/%m às %H:%M")
    if agente == "head":
        n = agora.replace(hour=8, minute=0, second=0, microsecond=0)
        dias = (7 - agora.weekday()) % 7
        n += datetime.timedelta(days=dias)
        if n <= agora:
            n += datetime.timedelta(days=7)
        return n.strftime("%d/%m às %H:%M")
    return "em até 30 minutos (confere se há briefing aprovado)"

def _hora(iso):
    try:
        return datetime.datetime.fromisoformat(iso).strftime("%H:%M")
    except Exception:
        return iso

def ler_status(agente):
    p = STATUS / f"{agente}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

def metricas():
    bl = (ROOT / "dados-mercado" / "backlog-notebooklm.md").read_text(encoding="utf-8")
    pend = len(re.findall(r"\| Pendente \|$", bl, flags=re.M))
    proc = len(re.findall(r"\| Processado \|$", bl, flags=re.M))
    desc = len(re.findall(r"\| Descartado \|$", bl, flags=re.M))
    dec = tabela(CONT / "decisoes-pauta.md")
    pautas_pend = sum(1 for _, c in dec if c[-1] == "Pendente")
    pautas_ok = sum(1 for _, c in dec if c[-1] == "Sim")
    return {"pend": pend, "proc": proc, "desc": desc, "pautas_pend": pautas_pend, "pautas_ok": pautas_ok}

def fmt_quando(iso):
    try:
        return datetime.datetime.fromisoformat(iso).strftime("%d/%m às %H:%M")
    except Exception:
        return iso

def html_resumo(linhas):
    m = metricas()
    ag_falhou = [AGENTES[k][0] for k in AGENTES if (ler_status(k) or {}).get("resultado") == "falhou"]
    ag_rodando = [AGENTES[k][0] for k in AGENTES if (ler_status(k) or {}).get("resultado") == "executando"]
    validar = sorted((int(re.search(r"\d+", c[0]).group()) for _, c in linhas if c[5] == "Em validação"), reverse=True)
    prod = {}
    pj = STATUS / "producao.json"
    if pj.exists():
        prod = json.loads(pj.read_text(encoding="utf-8"))
    em_producao = sorted(int(k) for k, e in prod.items() if "andamento" in e["etapas"].values())
    prod_falha = sorted(int(k) for k, e in prod.items() if "falhou" in e["etapas"].values() and "ok" not in (e["etapas"]["pagina"],))
    n_falhas = len(ag_falhou) + len(prod_falha)

    def tile(rotulo, n, classe):
        return f'<div class="rs-tile {classe}"><div class="rs-n">{n}</div><div class="rs-l">{rotulo}</div></div>'
    tiles = (tile("Briefings para aprovar", m["pautas_pend"], "rs-alerta" if m["pautas_pend"] else "rs-ok")
             + tile("Artigos para validar", len(validar), "rs-alerta" if validar else "rs-ok")
             + tile("Em produção", len(em_producao) + len(ag_rodando), "rs-info" if (em_producao or ag_rodando) else "rs-ok")
             + tile("Falhas", n_falhas, "rs-erro" if n_falhas else "rs-ok"))
    acoes = []
    if m["pautas_pend"]:
        acoes.append(f'<li><b>Aprovar {m["pautas_pend"]} briefing(s).</b> <a href="#status">Ver na aba Status</a> e responder no chat.</li>')
    if validar:
        links = ", ".join(f'<a href="#artigo-{n}" data-abrir="{n}">Artigo {n}</a>' for n in validar)
        acoes.append(f'<li><b>Validar {len(validar)} artigo(s):</b> {links}. Peça ajustes pelo código no chat.</li>')
    if m["pautas_ok"]:
        acoes.append(f'<li>{m["pautas_ok"]} briefing(s) aprovado(s) aguardando o Copywriter, que confere a fila a cada 30 minutos.</li>')
    if ag_rodando:
        acoes.append(f'<li>Em execução agora: {esc(", ".join(ag_rodando))}.</li>')
    if em_producao:
        acoes.append(f'<li>Artigos em produção: {esc(", ".join("Artigo " + str(n) for n in em_producao))}.</li>')
    if ag_falhou:
        acoes.append(f'<li class="rs-erro-txt"><b>Agente com falha:</b> {esc(", ".join(ag_falhou))}. Veja o log em ~/BXAI-logs no Mac.</li>')
    if prod_falha:
        acoes.append(f'<li class="rs-erro-txt"><b>Produção com falha:</b> {esc(", ".join("Artigo " + str(n) for n in prod_falha))}.</li>')
    lista = '<ul class="rs-lista">' + "".join(acoes) + "</ul>" if acoes else '<div class="rs-ok-txt">Nada pendente. Operação em dia.</div>'
    agora = _agora().strftime("%d/%m às %H:%M")
    base = (f'<div class="rs-base">Backlog: <b>{m["pend"]}</b> fontes pendentes, <b>{m["proc"]}</b> processadas, <b>{m["desc"]}</b> descartadas. '
            f'Painel gerado em {agora}.</div>')
    return f'<div class="resumo"><div class="section-label rs-titulo">Resumo da operação</div><div class="rs-tiles">{tiles}</div>{lista}{base}</div>'

def html_status():
    m = metricas()
    cards = []
    for chave, (nome, agenda) in AGENTES.items():
        s = ler_status(chave)
        linhas = []
        if not s:
            badge, cls = "Ainda não rodou", "idle"
            linhas.append("Sem execução registrada")
        elif s["resultado"] == "executando":
            badge, cls = "Em execução", "run"
            linhas.append(f'Iniciou às {esc(_hora(s["inicio"]))}, previsão de término às {esc(_hora(s["previsao"]))}')
            if s.get("resumo"):
                linhas.append(esc(s["resumo"]))
            ant = s.get("anterior") or {}
            if ant.get("quando"):
                linhas.append(f'Execução anterior: {esc(fmt_quando(ant["quando"]))}, {"concluída" if ant.get("resultado") == "ok" else "falhou"}')
        else:
            ok = s["resultado"] == "ok"
            badge, cls = ("Concluído" if ok else "Falhou"), ("ok" if ok else "bad")
            ini = f'Iniciou às {esc(_hora(s["inicio"]))}, terminou às {esc(_hora(s["quando"]))}' + (f' ({s["duracao_min"]} min)' if s.get("duracao_min") else "") if s.get("inicio") else f'Última execução: {esc(fmt_quando(s["quando"]))}'
            linhas.append(ini)
            resumo = s["resumo"] + (f" (commit {s['commit']})" if s.get("commit") else "")
            linhas.append(esc(resumo))
            linhas.append(f'Próxima execução: {esc(proxima_execucao(chave))}')
        corpo = "".join(f'<div class="ag-linha">{l}</div>' for l in linhas)
        cards.append(f'<div class="ag"><div class="ag-top"><span class="ag-nome">{esc(nome)}</span><span class="badge {cls}">{badge}</span></div>'
                     f'{corpo}<div class="ag-agenda">Agenda: {esc(agenda)}</div></div>')
    return '<div class="section-label">Status dos agentes</div><div class="agentes">' + "".join(cards) + "</div>"

ETAPAS = [("escrita", "Escrita"), ("revisao", "Revisão"), ("github", "No GitHub"), ("pagina", "Na página")]

def gravar_producao(cod, etapa=None, estado=None, msg="", titulo=""):
    STATUS.mkdir(exist_ok=True)
    p = STATUS / "producao.json"
    d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    e = d.setdefault(str(cod), {"titulo": titulo, "etapas": {k: "pendente" for k, _ in ETAPAS}, "msg": ""})
    if titulo:
        e["titulo"] = titulo
    if etapa == "escrita" and estado == "andamento":
        e["etapas"] = {k: "pendente" for k, _ in ETAPAS}
        e["etapas"]["escrita"] = "andamento"
        e["msg"] = ""
    elif etapa:
        e["etapas"][etapa] = estado
        if estado == "falhou":
            e["msg"] = msg
    e["quando"] = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

def html_producao():
    p = STATUS / "producao.json"
    if not p.exists():
        return ""
    d = json.loads(p.read_text(encoding="utf-8"))
    rotulo = {"ok": "concluída", "andamento": "em andamento", "falhou": "falhou", "pendente": "aguardando"}
    simbolo = {"ok": "&#10003;", "andamento": "&#9679;", "falhou": "&#10005;", "pendente": "&#9675;"}
    itens = []
    for cod in sorted(d, key=lambda x: -int(x))[:4]:
        e = d[cod]
        chips = '<span class="et et-ok">&#10003; Briefing aprovado</span>' + "".join(
            f'<span class="et et-{e["etapas"][k]}">{simbolo[e["etapas"][k]]} {nome}<small>{rotulo[e["etapas"][k]]}</small></span>' for k, nome in ETAPAS)
        erro = f'<div class="et-msg">{esc(e["msg"])}</div>' if e.get("msg") and "falhou" in e["etapas"].values() else ""
        itens.append(f'<div class="brief"><div class="brief-top"><span class="code">Artigo {esc(cod)}</span><span class="bf-data">atualizado {esc(fmt_quando(e.get("quando", "")))}</span></div>'
                     f'<div class="bf-tese">{esc(e.get("titulo", ""))}</div><div class="etapas">{chips}</div>{erro}</div>')
    return '<div class="section-label">Produção dos artigos</div>' + "".join(itens)

def html_briefings():
    itens = []
    for _, c in tabela(CONT / "decisoes-pauta.md"):
        ap = c[-1]
        if ap.startswith("Sim (Artigo"):
            continue
        tese = c[5] if len(c) > 6 else ""
        if tese.lower() == "a definir":
            tese = ""
        pend = ap == "Pendente"
        selo = "Aguardando sua aprovação" if pend else ("Aprovado, na fila do Copywriter" if ap == "Sim" else esc(ap))
        classe = "bf-pend" if pend else "bf-ok"
        itens.append(f'<div class="brief"><div class="brief-top"><span class="code">Briefing {esc(c[1])}</span><span class="tag">{esc(c[2])}</span><span class="bf {classe}">{selo}</span><span class="bf-data">semana {esc(c[0])}</span></div>'
                     + (f'<div class="bf-tese">{esc(tese)}</div>' if tese else '<div class="bf-tese bf-sem">Tese ainda não definida</div>')
                     + f'<div class="bf-linha"><b>Teoria base:</b> {esc(c[3])}</div><div class="bf-linha"><b>Apoio:</b> {esc(c[4])}</div></div>')
    corpo = "".join(itens) or '<div class="brief bf-vazio">Nenhum briefing aguardando. O Head monta 2 por semana, às segundas.</div>'
    return '<div class="section-label">Briefings para aprovar</div>' + corpo

def html_indice(linhas):
    itens = []
    for _, c in sorted(linhas, key=lambda x: -int(re.search(r"\d+", x[1][0]).group())):
        cod, titulo, pilar, status, arquivo = c[0], c[1], c[2], c[5], c[6]
        slug = pathlib.Path(arquivo).stem
        n = int(re.search(r"\d+", cod).group())
        links = (f'<a href="{GITHUB}conteudo/artigos/{slug}.md" target="_blank" rel="noopener">artigo</a> &middot; '
                 f'<a href="{GITHUB}conteudo/posts-linkedin/{slug}.md" target="_blank" rel="noopener">post</a> &middot; '
                 f'<a href="{GITHUB}conteudo/roteiros-video/{slug}.md" target="_blank" rel="noopener">roteiro</a> &middot; '
                 f'<a href="{GITHUB}conteudo/artes/{slug}.md" target="_blank" rel="noopener">arte</a>')
        itens.append(f'<li><span class="code">{esc(cod)}</span><div class="ix-txt"><a class="ix-titulo" href="#artigo-{n}" data-abrir="{n}">{esc(titulo)}</a>'
                     f'<div class="ix-meta"><span class="tag">{esc(pilar)}</span><span class="status">{esc(status)}</span><span class="ix-links">{links}</span></div></div></li>')
    return '<div class="section-label">Índice dos artigos</div><ul class="indice">' + "".join(itens) + "</ul>"

CSS = """
:root{--bg:#F4F6F6;--card:#FFFFFF;--border:#D9E3E1;--fg:#0F2A32;--muted:#53696D;--navy:#062D3E;--teal:#19B09F;--teal-soft:#E4F5F2;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#071A20;--card:#0D2832;--border:#1C3A42;--fg:#EAF3F2;--muted:#9FB8BA;--navy:#0A3A4E;--teal:#2BD6C2;--teal-soft:#113A38;color-scheme:dark;}}
:root[data-theme="dark"]{--bg:#071A20;--card:#0D2832;--border:#1C3A42;--fg:#EAF3F2;--muted:#9FB8BA;--navy:#0A3A4E;--teal:#2BD6C2;--teal-soft:#113A38;color-scheme:dark;}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--fg);font-family:Arial,Helvetica,sans-serif;}
.wrap{max-width:720px;margin:0 auto;padding:28px 16px 48px;padding-inline:16px;}
header{display:flex;align-items:center;gap:12px;margin-bottom:6px;}
.bar{width:6px;height:34px;background:var(--teal);border-radius:3px;flex:none;}
h1{font-size:22px;margin:0;letter-spacing:.2px;color:var(--fg);}
.sub{color:var(--muted);font-size:14px;margin:6px 0 28px 18px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;margin-bottom:14px;overflow:hidden;}
.card summary{list-style:none;cursor:pointer;padding:16px 18px;display:flex;align-items:flex-start;gap:12px;}
.card summary::-webkit-details-marker{display:none;}
.code{flex:none;background:var(--navy);color:#fff;font-size:12px;font-weight:bold;padding:4px 9px;border-radius:6px;letter-spacing:.3px;white-space:nowrap;margin-top:2px;}
.head-text{min-width:0;flex:1;}
.title{font-size:15.5px;font-weight:bold;line-height:1.35;color:var(--fg);}
.meta{display:flex;gap:8px;margin-top:7px;flex-wrap:wrap;}
.tag{font-size:11px;color:var(--muted);border:1px solid var(--border);border-radius:5px;padding:2px 7px;}
.status{font-size:11px;font-weight:bold;color:var(--teal);background:var(--teal-soft);border-radius:5px;padding:2px 7px;}
.chev{flex:none;color:var(--muted);transition:transform .15s ease;margin-top:6px;}
details[open] .chev{transform:rotate(90deg);}
.body{padding:0 18px 20px;}
.section-label{font-size:11px;font-weight:bold;letter-spacing:.6px;text-transform:uppercase;color:var(--teal);margin:18px 0 8px;}
.text p{font-size:14.5px;line-height:1.65;margin:0 0 12px;color:var(--fg);}
.text h3{font-size:14px;margin:14px 0 6px;color:var(--fg);}
.text h2{font-size:15.5px;margin:20px 0 8px;color:var(--fg);}
.source{font-size:12.5px;color:var(--muted);border-top:1px solid var(--border);padding-top:10px;margin-top:4px;}
.post-box{background:var(--teal-soft);border-radius:8px;padding:14px 16px;margin-top:4px;}
.post-box p{font-size:14px;line-height:1.6;margin:0 0 10px;color:var(--fg);}
.post-header{font-size:15px;font-weight:bold;line-height:1.5;margin:0 0 14px;color:var(--fg);}
.cut-marker{display:flex;align-items:center;gap:8px;margin:0 0 14px;font-size:10.5px;font-weight:bold;letter-spacing:.3px;text-transform:uppercase;color:var(--muted);}
.cut-marker::before,.cut-marker::after{content:"";flex:1;border-top:1px dashed var(--border);}
.video-box{border:1px dashed var(--border);border-radius:8px;padding:14px 16px;margin-top:4px;}
.video-box .block{margin-bottom:12px;}
.video-box .time{font-size:11px;font-weight:bold;color:var(--teal);}
.video-box .fala{font-size:14px;margin:3px 0;color:var(--fg);}

.agentes{display:grid;gap:10px;margin-bottom:12px;}
.ag{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:12px 14px;}
.ag-top{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:6px;}
.ag-nome{font-weight:bold;font-size:14.5px;}
.badge{font-size:11px;font-weight:bold;border-radius:5px;padding:2px 8px;}
.badge.ok{color:var(--teal);background:var(--teal-soft);}
.badge.bad{color:#B3261E;background:#FBE9E7;}
.badge.run{color:#7A4B00;background:#FFEFC9;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .badge.run{color:#FFD98A;background:#3A2C0A;}}
:root[data-theme="dark"] .badge.run{color:#FFD98A;background:#3A2C0A;}
.badge.idle{color:var(--muted);border:1px solid var(--border);}
.ag-linha{font-size:13px;line-height:1.5;color:var(--fg);}
.ag-agenda{font-size:12px;color:var(--muted);margin-top:4px;}
.metricas{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12.5px;color:var(--muted);margin:2px 0 26px;}
.metricas b{color:var(--fg);}
.etapas{display:flex;flex-wrap:wrap;gap:6px;}
.et{font-size:12px;border-radius:6px;padding:4px 9px;display:inline-flex;flex-direction:column;gap:1px;background:var(--bg);color:var(--muted);border:1px solid var(--border);}
.et small{font-size:10px;opacity:.85;}
.et-ok{color:var(--teal);background:var(--teal-soft);border-color:var(--teal-soft);}
.et-andamento{color:#7A4B00;background:#FFEFC9;border-color:#FFEFC9;}
.et-falhou{color:#8A1C1C;background:#FBDADA;border-color:#FBDADA;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .et-andamento{color:#FFD98A;background:#3A2C0A;border-color:#3A2C0A;}:root:not([data-theme="light"]) .et-falhou{color:#FFB4B4;background:#431616;border-color:#431616;}}
:root[data-theme="dark"] .et-andamento{color:#FFD98A;background:#3A2C0A;border-color:#3A2C0A;}
:root[data-theme="dark"] .et-falhou{color:#FFB4B4;background:#431616;border-color:#431616;}
.et-msg{font-size:12px;color:var(--muted);margin-top:8px;}
.brief{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px;margin-bottom:12px;}
.brief-top{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px;}
.bf{font-size:11px;font-weight:bold;border-radius:5px;padding:2px 7px;}
.bf-pend{color:#7A4B00;background:#FFEFC9;}
.bf-ok{color:var(--teal);background:var(--teal-soft);}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .bf-pend{color:#FFD98A;background:#3A2C0A;}}
:root[data-theme="dark"] .bf-pend{color:#FFD98A;background:#3A2C0A;}
.bf-data{font-size:12px;color:var(--muted);margin-left:auto;}
.bf-tese{font-size:15px;font-weight:bold;line-height:1.4;margin-bottom:8px;color:var(--fg);}
.bf-sem{color:var(--muted);font-weight:normal;font-style:italic;}
.bf-linha{font-size:13px;line-height:1.5;color:var(--muted);margin-top:4px;}
.bf-vazio{color:var(--muted);font-size:14px;}
.indice{list-style:none;margin:0 0 28px;padding:0;background:var(--card);border:1px solid var(--border);border-radius:10px;}
.indice li{display:flex;gap:12px;align-items:flex-start;padding:12px 16px;border-bottom:1px solid var(--border);}
.indice li:last-child{border-bottom:0;}
.ix-txt{min-width:0;}
.ix-titulo{font-size:14.5px;font-weight:bold;line-height:1.35;color:var(--fg);text-decoration:none;}
.ix-titulo:hover{color:var(--teal);text-decoration:underline;}
.ix-meta{display:flex;gap:8px;margin-top:6px;flex-wrap:wrap;align-items:center;}
.ix-links{font-size:12px;color:var(--muted);}
.ix-links a{color:var(--teal);text-decoration:none;}
.ix-links a:hover{text-decoration:underline;}
.card{scroll-margin-top:12px;}
.dl{display:inline-block;background:var(--teal);color:var(--navy);text-decoration:none;font-size:13px;font-weight:bold;padding:8px 14px;border-radius:6px;margin:0 6px 10px 0;}
details.sub{border:1px solid var(--border);border-radius:8px;margin:8px 0;padding:0 14px;}
details.sub>summary{cursor:pointer;padding:10px 0;font-size:13.5px;font-weight:bold;color:var(--fg);}
details.sub[open]{padding-bottom:12px;}
.arte-box{border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin-top:4px;}
.arte-linha{font-size:13.5px;line-height:1.55;margin-bottom:6px;color:var(--fg);}
.arte-prompt{background:var(--teal-soft);border-radius:8px;padding:12px 14px;margin-top:10px;}
.arte-prompt p{font-size:13.5px;line-height:1.6;margin:8px 0 0;color:var(--fg);}
.arte-top{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:13px;color:var(--fg);}
.copiar{font:inherit;font-size:12px;font-weight:bold;border-radius:6px;padding:4px 10px;cursor:pointer;background:var(--card);color:var(--teal);border:1px solid var(--border);}
.copiar:focus-visible{outline:2px solid var(--teal);outline-offset:2px;}
.resumo{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px;margin:0 0 22px;}
.rs-titulo{margin:0 0 10px;}
.rs-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:12px;}
.rs-tile{border-radius:8px;padding:10px 12px;border:1px solid var(--border);background:var(--bg);}
.rs-n{font-size:24px;font-weight:bold;line-height:1.1;font-variant-numeric:tabular-nums;}
.rs-l{font-size:12px;color:var(--muted);margin-top:3px;}
.rs-ok .rs-n{color:var(--muted);}
.rs-alerta{background:#FFEFC9;border-color:#FFEFC9;}
.rs-alerta .rs-n,.rs-alerta .rs-l{color:#7A4B00;}
.rs-erro{background:#FBDADA;border-color:#FBDADA;}
.rs-erro .rs-n,.rs-erro .rs-l{color:#8A1C1C;}
.rs-info{background:var(--teal-soft);border-color:var(--teal-soft);}
.rs-info .rs-n{color:var(--teal);}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .rs-alerta{background:#3A2C0A;border-color:#3A2C0A;}:root:not([data-theme="light"]) .rs-alerta .rs-n,:root:not([data-theme="light"]) .rs-alerta .rs-l{color:#FFD98A;}:root:not([data-theme="light"]) .rs-erro{background:#431616;border-color:#431616;}:root:not([data-theme="light"]) .rs-erro .rs-n,:root:not([data-theme="light"]) .rs-erro .rs-l{color:#FFB4B4;}}
:root[data-theme="dark"] .rs-alerta{background:#3A2C0A;border-color:#3A2C0A;}
:root[data-theme="dark"] .rs-alerta .rs-n,:root[data-theme="dark"] .rs-alerta .rs-l{color:#FFD98A;}
:root[data-theme="dark"] .rs-erro{background:#431616;border-color:#431616;}
:root[data-theme="dark"] .rs-erro .rs-n,:root[data-theme="dark"] .rs-erro .rs-l{color:#FFB4B4;}
.rs-lista{margin:0 0 10px;padding-left:18px;font-size:13.5px;line-height:1.6;}
.rs-lista a{color:var(--teal);}
.rs-erro-txt{color:#B3261E;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .rs-erro-txt{color:#FFB4B4;}}
:root[data-theme="dark"] .rs-erro-txt{color:#FFB4B4;}
.rs-ok-txt{font-size:13.5px;color:var(--muted);margin-bottom:10px;}
.rs-base{font-size:12px;color:var(--muted);}
.abas{display:flex;gap:8px;margin:0 0 22px 18px;}
.aba{font:inherit;font-size:14px;font-weight:bold;border-radius:8px;padding:8px 18px;cursor:pointer;background:var(--card);color:var(--muted);border:1px solid var(--border);}
.aba:hover{color:var(--fg);}
.aba:focus-visible{outline:2px solid var(--teal);outline-offset:2px;}
.aba-on{background:var(--navy);color:#fff;border-color:var(--navy);}
.footer-note{color:var(--muted);font-size:12.5px;text-align:center;margin-top:24px;line-height:1.6;}
"""

def esc(s):
    return html.escape(s, quote=False)

def blocos(texto):
    return [b.strip() for b in re.split(r"\n\s*\n", texto.strip()) if b.strip()]

def html_artigo(slug):
    return html_artigo_txt(caminhos(slug)[0].read_text(encoding="utf-8"))

def html_artigo_txt(t):
    t = re.sub(r"^#.*\n", "", t, count=1)
    out = []
    for b in blocos(t):
        if b.startswith("### "):
            out.append(f"<h3>{esc(b[4:].strip())}</h3>")
        elif b.startswith("## "):
            out.append(f"<h2>{esc(b[3:].strip())}</h2>")
        elif re.match(r"(Fonte|Fontes|Source|Sources|Fuente|Fuentes):", b):
            out.append(f'<div class="source">{esc(b)}</div>')
        else:
            out.append(f"<p>{_links_html(esc(' '.join(b.splitlines())))}</p>")
    return "\n".join(out)

def html_post(slug):
    return html_post_txt(caminhos(slug)[1].read_text(encoding="utf-8"))

def html_post_txt(texto):
    linhas = texto.splitlines()
    cab = linhas[0].strip()
    resto = "\n".join(x for x in linhas[1:] if x.strip() != ".")
    ps = "\n".join(f"<p>{_links_html(esc('<br>'.join(b.splitlines())).replace('&lt;br&gt;', '<br>'))}</p>" for b in blocos(resto))
    return (f'<div class="post-box"><div class="post-header">{esc(cab)}</div>'
            f'<div class="cut-marker">corte do "ver mais" no LinkedIn</div>\n{ps}</div>')

def html_arte(slug):
    p = CONT / "artes" / f"{slug}.md"
    if not p.exists():
        return ""
    t = p.read_text(encoding="utf-8")
    prompt = t.split("Prompt:", 1)[1].strip() if "Prompt:" in t else ""
    campos = re.findall(r"^(Formato|Frase de destaque|Dado central|Composição|Paleta e tipografia|Fonte na imagem):\s*(.+)$", t, flags=re.M)
    linhas = "".join(f'<div class="arte-linha"><b>{esc(k)}:</b> {esc(v)}</div>' for k, v in campos)
    return (f'<div class="section-label">Sugestão de arte</div><div class="arte-box">{linhas}'
            f'<div class="arte-prompt"><div class="arte-top"><b>Prompt</b><button type="button" class="copiar">Copiar prompt</button></div><p>{esc(prompt)}</p></div></div>')

def html_roteiro(slug):
    return html_roteiro_txt(caminhos(slug)[2].read_text(encoding="utf-8"))

def html_roteiro_txt(t):
    achados = re.findall(r"\*\*(.+?)\*\*\s*\n(.+?)(?=\n\s*\n|\Z)", t, flags=re.S)
    blocos_html = "".join(f'<div class="block"><div class="time">{esc(h.strip())}</div><div class="fala">{esc(" ".join(f.split()))}</div></div>' for h, f in achados)
    return f'<div class="video-box">{blocos_html}</div>'

def html_seo(seo):
    def lin(k, v):
        return f'<div class="arte-linha"><b>{esc(k)}:</b> {esc(v)}</div>'
    faq = "".join(f'<div class="arte-linha"><b>{esc(x["pergunta"])}</b><br>{esc(x["resposta"])}</div>' for x in seo.get("faq", []))
    return ('<div class="arte-box">'
            + lin("Palavra-chave", seo.get("palavra_chave", ""))
            + lin("Secundárias", ", ".join(seo.get("palavras_secundarias", [])))
            + lin(f"Título SEO ({len(seo.get('titulo_seo', ''))} caracteres)", seo.get("titulo_seo", ""))
            + lin(f"Meta descrição ({len(seo.get('meta_descricao', ''))} caracteres)", seo.get("meta_descricao", ""))
            + lin("Slug", seo.get("slug_url", ""))
            + lin("Resumo do card (excerpt)", seo.get("excerpt", ""))
            + lin("Neste artigo", seo.get("neste_artigo", ""))
            + lin("Resumo GEO", seo.get("resumo_geo", ""))
            + lin("Entidades", ", ".join(seo.get("entidades", [])))
            + f'<div class="section-label">FAQ</div>{faq}</div>')

def html_idiomas(slug):
    import base64
    arqs = montar_json(slug)
    if not arqs:
        return ""
    d = ler_idiomas(slug)
    botoes = "".join(f'<a class="dl" download="{esc(arqs[lg].name)}" href="data:application/json;base64,{base64.b64encode(arqs[lg].read_bytes()).decode()}">Baixar JSON {NOMES_IDIOMA[lg]}</a> ' for lg in ("pt", "en", "es"))
    saida = [f'<div class="section-label">Idiomas, SEO e GEO</div>{botoes}']
    for lg in ("en", "es"):
        x = d[lg]
        saida.append(f'<details class="sub"><summary>{NOMES_IDIOMA[lg]}: {esc(x["titulo"])}</summary>'
                     f'<div class="section-label">Artigo</div><div class="text">{html_artigo_txt("# t" + chr(10) + x["artigo"])}</div>'
                     f'<div class="section-label">Post LinkedIn</div>{html_post_txt(x["post"])}'
                     f'<div class="section-label">Roteiro de vídeo</div>{html_roteiro_txt(x["roteiro"])}</details>')
    for lg in ("pt", "en", "es"):
        saida.append(f'<details class="sub"><summary>Relatório de SEO e GEO, {NOMES_IDIOMA[lg]}</summary>{html_seo(d[lg]["seo"])}</details>')
    return "\n".join(saida)

JS = r'''function aba(n){["status","artigos"].forEach(function(x){document.getElementById("aba-"+x).hidden=(x!==n);var b=document.getElementById("btn-"+x);b.setAttribute("aria-selected",x===n?"true":"false");b.classList.toggle("aba-on",x===n);});try{if(history.replaceState&&n!==location.hash.slice(1)&&!/^#artigo-/.test(location.hash))history.replaceState(null,"","#"+n);}catch(e){}}
function abrir(){var h=location.hash;if(!h)return;if(h==="#status"||h==="#artigos"){aba(h.slice(1));return;}var e=document.querySelector(h);if(e&&e.tagName==="DETAILS"){aba("artigos");e.open=true;e.scrollIntoView();}}
document.addEventListener("click",function(ev){var t=ev.target.closest("button[data-aba]");if(t){aba(t.dataset.aba);return;}var a=ev.target.closest("a[data-abrir]");if(!a)return;ev.preventDefault();var e=document.getElementById("artigo-"+a.dataset.abrir);if(e){aba("artigos");e.open=true;e.scrollIntoView({behavior:"smooth"});}});
document.addEventListener("click",function(ev){var c=ev.target.closest("button.copiar");if(!c)return;var txt=c.closest(".arte-prompt").querySelector("p").innerText;var ok=function(){c.textContent="Copiado";setTimeout(function(){c.textContent="Copiar prompt";},1500);};var fb=function(){var r=document.createRange();r.selectNodeContents(c.closest(".arte-prompt").querySelector("p"));var s=window.getSelection();s.removeAllRanges();s.addRange(r);c.textContent="Selecionado, copie com Ctrl+C";};try{navigator.clipboard.writeText(txt).then(ok,fb);}catch(e){fb();}});
window.addEventListener("hashchange",abrir);aba("status");abrir();
if(/github\.io$/.test(location.hostname)){setInterval(function(){if(!document.hidden&&!document.getElementById("aba-status").hidden)location.reload();},60000);}'''


def gerar_pagina():
    cards = []
    linhas = indice()
    codigos = sorted((int(re.search(r"\d+", c[0]).group()) for _, c in linhas), reverse=True)
    abertos = set(codigos[:2])
    for _, c in sorted(linhas, key=lambda x: -int(re.search(r"\d+", x[1][0]).group())):
        cod, titulo, pilar, status, arquivo = c[0], c[1], c[2], c[5], c[6]
        slug = pathlib.Path(arquivo).stem
        n = int(re.search(r"\d+", cod).group())
        aberto = " open" if n in abertos else ""
        cards.append(f"""<details class="card" id="artigo-{n}"{aberto}><summary><span class="code">{esc(cod)}</span><span class="head-text"><div class="title">{esc(titulo)}</div><div class="meta"><span class="tag">{esc(pilar)}</span><span class="status">{esc(status)}</span></div></span><span class="chev">&#8250;</span></summary>
<div class="body"><div class="section-label">Artigo</div><div class="text">{html_artigo(slug)}</div>
<div class="section-label">Post LinkedIn</div>{html_post(slug)}
<div class="section-label">Roteiro de vídeo (1 minuto, Daniel falando para a câmera)</div>{html_roteiro(slug)}
{html_arte(slug)}
{html_idiomas(slug)}</div></details>""")
    pagina = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Artigos BXAI</title><style>{CSS}</style></head><body>
<div class="wrap"><header><div class="bar"></div><h1>BudgetXpert, squad de conteúdo</h1></header>
<div class="sub">Referencie pelo código ao pedir ajustes no chat</div>
{html_resumo(linhas)}
<div class="abas" role="tablist"><button type="button" class="aba" id="btn-status" role="tab" data-aba="status">Status</button><button type="button" class="aba" id="btn-artigos" role="tab" data-aba="artigos">Artigos</button></div>
<section id="aba-status" role="tabpanel">
{html_status()}
{html_briefings()}
{html_producao()}
</section>
<section id="aba-artigos" role="tabpanel" hidden>
{html_indice(linhas)}
<div class="section-label">Artigos</div>
{chr(10).join(cards)}
</section>
<div class="footer-note">Peça ajustes citando o código, por exemplo "Artigo 1, refaça a abertura".<br>O conteúdo completo e o histórico ficam no repositório daninaka-hub/BXAI.</div></div><script>{JS}</script></body></html>"""
    PAGINA.parent.mkdir(exist_ok=True)
    PAGINA.write_text(pagina, encoding="utf-8")
    old = PAGINA.parent / "status.html"
    if old.exists():
        old.unlink()

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "listar":
        print(json.dumps(listar(), ensure_ascii=False))
    elif cmd == "lint":
        e = lint(sys.argv[2]); print("\n".join(e)); sys.exit(1 if [x for x in e if not x.startswith("aviso:")] else 0)
    elif cmd == "status":
        gravar_status(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "")
    elif cmd == "status-inicio":
        iniciar_status(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "", int(sys.argv[4]) if len(sys.argv) > 4 else None)
    elif cmd == "producao":
        a = sys.argv[2:] + [""] * 5
        gravar_producao(a[0], a[1] or None, a[2] or None, a[3], a[4])
    elif cmd == "json":
        print(montar_json(sys.argv[2]))
    elif cmd == "gerar-pagina":
        gerar_pagina(); print(PAGINA)
