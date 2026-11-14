# praxis toolbox — the canonical interface. Self-documenting: `make help`.
.PHONY: help lint test build sync

help: ## list targets
	@awk -F':.*## ' '/^[a-zA-Z][a-zA-Z0-9_-]*:.*## /{printf "  make %-14s %s\n", $$1, $$2}' Makefile

lint: ## zero-token toolbox health check
	@bash tools/tb-lint.sh .

test: lint ## lint + every toolbox test
	@rc=0; for t in tests/test-*.sh; do [ -e "$$t" ] || continue; echo "== $$t"; bash "$$t" || rc=1; done; exit $$rc

build: ## build all src/ tools (toolsmith adds per-tool build-<name> targets)
	@true

sync: ## mirror skills/ into .claude/skills/ (marker-guarded)
	@bash tools/tb-sync-skills.sh .
