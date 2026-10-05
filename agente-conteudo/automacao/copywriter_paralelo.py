#!/usr/bin/env python3
"""Produz em paralelo os artigos dos briefings aprovados, publica no GitHub e atualiza a página de validação.
Roda sozinho (launchd, a cada 30 minutos). Sem briefing aprovado, sai em silêncio."""
import os, sys, subprocess, pathlib, shutil, datetime, time
from concurrent.futures import ThreadPoolExecutor

HOME = pathlib.Path.home()
REPO = HOME / "BXAI"
WT = HOME / "BXAI-wt"
LOGS = HOME / "BXAI-logs"
AUTO = REPO / "agente-conteudo" / "automacao"
CLAUDE_TOOLS = "Read,Glob,Grep,Write,Edit"
os.environ["PATH"] = f"{HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH", "")
LOGS.mkdir(exist_ok=True)
LOG = LOGS / f"{datetime.date.today()}-copywriter.log"

def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%H:%M:%S}] {msg}\n")

def notificar(titulo, texto):
    texto = texto.replace('"', "'")[:180]
    subprocess.run(["osascript", "-e", f'display notification "{texto}" with title "BXAI: {titulo}"'], capture_output=True)

def sh(cmd, cwd=REPO, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    log(f"$ {' '.join(cmd)}\n{r.stdout}{r.stderr}".rstrip())
    if check and r.returncode != 0:
        raise RuntimeError(f"comando falhou: {' '.join(cmd)}\n{r.stderr.strip()}")
    return r

def claude(prompt, cwd, tools=CLAUDE_TOOLS):
    r = subprocess.run(["caffeinate", "-i", "claude", "-p", prompt, "--permission-mode", "acceptEdits", "--allowedTools", tools],
                       cwd=cwd, capture_output=True, text=True)
    log(f"claude em {cwd.name}, código {r.returncode}\n{r.stdout[-1500:]}{r.stderr[-800:]}")
    if r.returncode != 0:
        raise RuntimeError(f"o Claude Code terminou com erro {r.returncode}")
    return r.stdout

def squad(*args):
    return subprocess.run([sys.executable, str(AUTO / "squad.py"), *args], cwd=REPO, capture_output=True, text=True)

def preparar(b):
    """Cria a cópia de trabalho do artigo. Roda em sequência, porque o git trava a configuração se duas cópias nascem juntas."""
    cod = b["codigo"]
    wt = WT / f"artigo-{cod}"
    if wt.exists():
        sh(["git", "worktree", "remove", "--force", str(wt)], check=False)
    sh(["git", "branch", "-D", f"artigo-{cod}"], check=False)
    sh(["git", "worktree", "add", "--no-track", "-b", f"artigo-{cod}", str(wt), "origin/main"])
    return wt

def produzir(b, wt):
    prompt = (AUTO / "prompt-copywriter.md").read_text(encoding="utf-8")
    for k, v in {"{SLUG}": b["slug"], "{CODIGO}": str(b["codigo"]), "{PILAR}": b["pilar"], "{TEORIA}": b["teoria"], "{APOIO}": b["apoio"]}.items():
        prompt = prompt.replace(k, v)
    claude(prompt, wt)
    return wt

def lint_em(wt, slug):
    env = dict(os.environ)
    r = subprocess.run([sys.executable, str(wt / "agente-conteudo" / "automacao" / "squad.py"), "lint", slug], cwd=wt, capture_output=True, text=True, env=env)
    return [x for x in r.stdout.splitlines() if x.strip()]

def main():
    lock = HOME / ".bxai-copywriter.lock"
    try:
        os.mkdir(lock)
    except FileExistsError:
        if time.time() - lock.stat().st_mtime < 4 * 3600:
            return
        shutil.rmtree(lock, ignore_errors=True); os.mkdir(lock)
    try:
        if not (REPO / ".git").exists():
            return
        sh(["git", "pull", "--rebase", "origin", "main"])
        briefs = __import__("json").loads(squad("listar").stdout or "[]")
        if not briefs:
            return
        log(f"=== {len(briefs)} briefing(s) aprovado(s): {[b['codigo'] for b in briefs]} ===")
        WT.mkdir(exist_ok=True)
        sh(["git", "fetch", "origin"])
        resultados = {}
        pastas = {}
        for b in briefs:
            try:
                pastas[b["codigo"]] = preparar(b)
            except Exception as e:
                resultados[b["codigo"]] = e
                log(f"Artigo {b['codigo']} falhou ao preparar a pasta: {e}")
        com_pasta = [b for b in briefs if b["codigo"] in pastas]
        if com_pasta:
            with ThreadPoolExecutor(max_workers=len(com_pasta)) as ex:
                futs = {b["codigo"]: ex.submit(produzir, b, pastas[b["codigo"]]) for b in com_pasta}
                for cod, f in futs.items():
                    try:
                        resultados[cod] = f.result()
                    except Exception as e:
                        resultados[cod] = e
                        log(f"Artigo {cod} falhou: {e}")

        boas = []
        for b in briefs:
            wt = resultados[b["codigo"]]
            if isinstance(wt, Exception):
                continue
            erros = lint_em(wt, b["slug"])
            if erros:
                log(f"Artigo {b['codigo']}: {len(erros)} problema(s), uma rodada de correção")
                try:
                    claude("Corrija somente os problemas abaixo nos arquivos do artigo {s} (artigo, post e roteiro), sem mudar o resto, sem travessão e sem vírgula seguida de e. Responda só PRONTO.\n\n".replace("{s}", b["slug"]) + "\n".join(erros), wt)
                    erros = lint_em(wt, b["slug"])
                except Exception as e:
                    log(f"correção falhou: {e}")
            if erros:
                log(f"Artigo {b['codigo']} reprovado no lint:\n" + "\n".join(erros))
                resultados[b["codigo"]] = RuntimeError("reprovado no lint")
            else:
                boas.append(b)

        for b in boas:
            wt = resultados[b["codigo"]]
            for rel in (f"conteudo/artigos/{b['slug']}.md", f"conteudo/posts-linkedin/{b['slug']}.md", f"conteudo/roteiros-video/{b['slug']}.md"):
                dest = REPO / "agente-conteudo" / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(wt / "agente-conteudo" / rel, dest)

        for b in sorted(boas, key=lambda x: x["codigo"]):
            import importlib.util
            spec = importlib.util.spec_from_file_location("squad", AUTO / "squad.py"); sq = importlib.util.module_from_spec(spec); spec.loader.exec_module(sq)
            sq.indexar(b["codigo"], b["slug"], sq.titulo_do_artigo(b["slug"]), b["pilar"], b["teoria"], b["apoio"])
            sq.marcar(b["linha"], f"Sim (Artigo {b['codigo']})")
        for b in briefs:
            if isinstance(resultados[b["codigo"]], Exception):
                import importlib.util
                spec = importlib.util.spec_from_file_location("squad", AUTO / "squad.py"); sq = importlib.util.module_from_spec(spec); spec.loader.exec_module(sq)
                sq.marcar(b["linha"], "Sim (falhou na produção, ver log)")

        squad("gerar-pagina")
        sh(["git", "add", "agente-conteudo"])
        codigos = ", ".join(str(b["codigo"]) for b in boas) or "nenhum"
        sh(["git", "commit", "-m", f"Copywriter: artigos {codigos} produzidos em paralelo e página de validação atualizada"], check=False)
        sh(["git", "push", "origin", "HEAD:main"])
        sh(["git", "fetch", "origin"])
        head = sh(["git", "rev-parse", "HEAD"]).stdout.strip()
        if head != sh(["git", "rev-parse", "origin/main"]).stdout.strip():
            raise RuntimeError("o commit não chegou ao origin/main")

        for b in briefs:
            wt = resultados[b["codigo"]]
            if not isinstance(wt, Exception):
                sh(["git", "worktree", "remove", "--force", str(wt)], check=False)
            sh(["git", "branch", "-D", f"artigo-{b['codigo']}"], check=False)

        publicado = "não tentado"
        if boas:
            try:
                saida = claude((AUTO / "prompt-publicar.md").read_text(encoding="utf-8"), REPO, tools="Read,Artifact")
                publicado = "PUBLICADO" if "PUBLICADO" in saida else saida.strip()[:120]
            except Exception as e:
                publicado = f"erro: {e}"
        falhas = [b["codigo"] for b in briefs if isinstance(resultados[b["codigo"]], Exception)]
        msg = f"Artigos {codigos} prontos. Página: {publicado}."
        if falhas:
            msg += f" Falharam: {falhas}."
        if publicado != "PUBLICADO" and boas:
            msg += " Peça no chat: publique a página de artigos."
        log(msg)
        notificar("Copywriter concluído" if not falhas else "Copywriter com falhas", msg)
    except Exception as e:
        log(f"FALHA: {e}")
        notificar("Copywriter falhou", str(e).splitlines()[0])
        sys.exit(1)
    finally:
        shutil.rmtree(lock, ignore_errors=True)

if __name__ == "__main__":
    main()
