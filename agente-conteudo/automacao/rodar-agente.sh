#!/bin/bash
# Roda um agente do squad BXAI (pesquisador ou head) e confere se o push chegou ao GitHub.
# Uso: rodar-agente.sh pesquisador|head
set -u
EXTRA="$(cat "$HOME/.bxai-path" 2>/dev/null)"
export PATH="${EXTRA:+$EXTRA:}$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

AGENTE="${1:-}"
REPO="$HOME/BXAI"
LOGS="$HOME/BXAI-logs"
mkdir -p "$LOGS"
LOG="$LOGS/$(date +%Y-%m-%d)-${AGENTE:-sem-agente}.log"

notificar() { osascript -e "display notification \"$2\" with title \"BXAI: $1\"" >/dev/null 2>&1; }
# Atualiza o painel de status e republica a página (melhor esforço, nunca derruba o agente)
painel() {
  [ -d "$REPO/.git" ] || return 0
  ( cd "$REPO" &&
    python3 agente-conteudo/automacao/squad.py status "$AGENTE" "$1" "$2" "${3:-}" &&
    python3 agente-conteudo/automacao/squad.py gerar-pagina &&
    git add agente-conteudo/status agente-conteudo/validacao &&
    git commit -q -m "Painel: status do $AGENTE ($1)" &&
    git pull -q --rebase --autostash origin main &&
    git push -q origin HEAD:main ) >> "$LOG" 2>&1 || git rebase --abort >> "$LOG" 2>&1 || true
  # A página é servida pelo GitHub Pages, então o push já atualiza o painel
}
falha() { echo "FALHA: $1" | tee -a "$LOG"; painel falhou "$1"; notificar "$AGENTE falhou" "$1"; exit 1; }

case "$AGENTE" in
  pesquisador|head) ;;
  *) echo "uso: $0 pesquisador|head"; exit 2 ;;
esac

echo "=== $(date '+%d/%m/%Y %H:%M:%S') início: $AGENTE ===" >> "$LOG"

command -v claude >/dev/null 2>&1 || falha "Claude Code não encontrado no PATH. Rode de novo o instalar.sh"
if [ ! -d "$REPO/.git" ]; then
  git clone https://github.com/daninaka-hub/BXAI "$REPO" >> "$LOG" 2>&1 || falha "clone do repositório falhou"
fi
cd "$REPO" || falha "pasta $REPO não existe"
git rebase --abort >> "$LOG" 2>&1 || true
git fetch -q origin >> "$LOG" 2>&1 || falha "git fetch falhou (sem rede)"
git checkout -q -f -B main origin/main >> "$LOG" 2>&1 || falha "não consegui voltar o clone para o origin/main"
# Registra o início da execução no painel (só git, sem chamar o Claude)
python3 agente-conteudo/automacao/squad.py status-inicio "$AGENTE" "Em execução" >> "$LOG" 2>&1 &&
  git add agente-conteudo/status && git commit -q -m "Painel: $AGENTE iniciou" >> "$LOG" 2>&1 &&
  git push -q origin HEAD:main >> "$LOG" 2>&1 || true
ANTES=$(git rev-parse HEAD)

PROMPT_FILE="agente-conteudo/automacao/prompt-$AGENTE.md"
[ -f "$PROMPT_FILE" ] || falha "prompt $PROMPT_FILE não encontrado"

caffeinate -i claude -p "$(cat "$PROMPT_FILE")" \
  --permission-mode acceptEdits \
  --allowedTools "Bash(git *),Bash(date *),Bash(ls *),Read,Edit,Write,WebSearch,WebFetch,Agent" \
  >> "$LOG" 2>&1
RC=$?
[ "$RC" -eq 0 ] || falha "o Claude Code terminou com erro $RC (veja $LOG)"

# Conferência independente: o commit precisa estar no GitHub
git fetch -q origin >> "$LOG" 2>&1 || falha "git fetch falhou na conferência"
[ -z "$(git status --porcelain)" ] || falha "sobraram alterações sem commit"
[ "$(git rev-parse HEAD)" != "$ANTES" ] || falha "o agente não gerou nenhum commit novo"
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
  git push origin HEAD:main >> "$LOG" 2>&1 || falha "git push falhou (veja $LOG)"
  git fetch -q origin
fi
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || falha "o commit não chegou ao origin/main"

HASH=$(git rev-parse --short HEAD)
painel ok "Rodada concluída" "$HASH"
echo "OK: commit $HASH no origin/main às $(date '+%H:%M:%S')" | tee -a "$LOG"
notificar "$AGENTE concluído" "Commit $HASH publicado no GitHub"
