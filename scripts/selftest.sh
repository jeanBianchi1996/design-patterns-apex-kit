#!/usr/bin/env bash
# Valida estrutura do plugin, conteúdo do catálogo e o detector de smells.
set -euo pipefail

KIT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$KIT"

for json in .claude-plugin/plugin.json .claude-plugin/marketplace.json hooks/hooks.json; do
  python3 -m json.tool "$json" > /dev/null
done

expected=22
count=$(find knowledge/criacionais knowledge/estruturais knowledge/comportamentais -name "*.md" | wc -l)
if [ "$count" -ne "$expected" ]; then
  echo "Catálogo incompleto: $count de $expected padrões" >&2
  exit 1
fi

for skill in skills/*/SKILL.md; do
  head -1 "$skill" | grep -q '^---$' || { echo "Frontmatter ausente: $skill" >&2; exit 1; }
  grep -q '^name:' "$skill" && grep -q '^description:' "$skill" || { echo "name/description ausente: $skill" >&2; exit 1; }
done

# As classes reutilizáveis do kit devem estar livres de smells.
output=$(python3 hooks/scripts/design_smells.py templates/classes)
echo "$output" | tail -1
echo "$output" | grep -q "^0 design smell" || { echo "$output" >&2; exit 1; }

# O detector precisa encontrar smells num exemplo ruim.
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
cat > "$WORK/BadPricing.cls" <<'APEX'
public class BadPricing {
    public Decimal shipping(String carrier, String state, Decimal a, Decimal b, Decimal c) {
        if (carrier == 'A') { return 1; }
        else if (carrier == 'B') { return 2; }
        else if (carrier == 'C') { return 3; }
        else if (carrier == 'D') { return 4; }
        return new TaxService().calculate(a);
    }
}
APEX
bad=$(python3 hooks/scripts/design_smells.py "$WORK")
for rule in DSN003 DSN004 DSN008; do
  echo "$bad" | grep -q "$rule" || { echo "Detector não encontrou $rule" >&2; echo "$bad" >&2; exit 1; }
done
echo "selftest OK"
