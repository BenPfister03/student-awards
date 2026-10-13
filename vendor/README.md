# Vendored third-party libraries

These files are committed so diagram and PDF export work without downloading
binaries at runtime. Refresh them only when bumping a version; keep
`vendor/manifest.json` in sync (sha256).

| Path | Version | License | Upstream |
|------|---------|---------|----------|
| `vendor/plantuml/plantuml.jar` | PlantUML MIT 1.2026.7 | MIT | [GitHub release](https://github.com/plantuml/plantuml/releases/tag/v1.2026.7) (`plantuml-mit-1.2026.7.jar`) |
| `vendor/fonts/DejaVuSans*.ttf` | DejaVu 2.37 | Bitstream Vera / Arev (see `LICENSE`) | [dejavu-fonts 2.37](https://github.com/dejavu-fonts/dejavu-fonts/releases/tag/version_2_37) |

Python packages are pinned in `requirements.txt` (`pip install -r requirements.txt`). No Poetry.
Mermaid CLI is pinned in `package-lock.json`.

## Refresh PlantUML

```bash
curl -L -o vendor/plantuml/plantuml.jar \
  https://github.com/plantuml/plantuml/releases/download/v1.2026.7/plantuml-mit-1.2026.7.jar
```

Then rewrite `vendor/manifest.json` hashes. `python manage.py usecase` verifies
the JAR checksum before it runs Java.

Use-case rendering needs a JRE (`java` on `PATH` or `JAVA_HOME`). Graphviz is
not required: the command uses PlantUML’s bundled Smetana layout.
