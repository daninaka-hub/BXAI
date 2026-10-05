#!/bin/bash
# Instala os dois agendamentos do squad BXAI no macOS (launchd).
set -e
DIR="$HOME/BXAI/agente-conteudo/automacao"
DEST="$HOME/Library/LaunchAgents"
mkdir -p "$DEST" "$HOME/BXAI-logs"
chmod +x "$DIR/rodar-agente.sh"
command -v claude >/dev/null 2>&1 || { echo "Claude Code não encontrado. Instale e faça login antes."; exit 1; }
for nome in pesquisador head copywriter; do
  P="com.budgetxpert.bxai.$nome"
  launchctl bootout "gui/$(id -u)/$P" 2>/dev/null || true
  cp "$DIR/$P.plist" "$DEST/$P.plist"
  launchctl bootstrap "gui/$(id -u)" "$DEST/$P.plist"
  echo "Instalado: $P"
done
echo "Pronto. Pesquisador todo dia às 7h, Head de Conteúdo às segundas às 8h, Copywriter a cada 30 minutos (só age quando há briefing aprovado)."
echo "Para testar agora: launchctl kickstart gui/$(id -u)/com.budgetxpert.bxai.pesquisador"
echo "Logs em: $HOME/BXAI-logs"
