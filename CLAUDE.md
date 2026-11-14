# Setara repository

The project lives in `setara/`; its rules, layout and commands are in
`setara/CLAUDE.md`. Read that first.

<!-- praxis:begin -->
## Toolbox
This project has an agent-managed toolbox (tools + skills). Before writing
scripts or pipelines, check `toolbox/index.md`. Interface: `make -C toolbox
help` (lint / test / build / sync). Conventions: praxis:toolbox skill.
Tool ideas: one line in `toolbox/.wishes`. Cleanup: /praxis:retire.
<!-- praxis:end -->
