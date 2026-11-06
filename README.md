# Cia. de Rafting — novo site

A página principal (`index.html`) é um índice com atalhos para cada revisão. Cada pasta é um site completo e independente:

- `rev0/` — primeira versão: tema escuro, página única (home longa).
- `rev1/` — mesma estrutura da rev0 com visual claro e sóbrio.
- `rev2/` — fiel ao site original do Wix: 12 páginas, mesmo menu e textos, modernizada e responsiva, com painel de edição (Pages CMS; ver `rev2/GUIA-DE-EDICAO.md`).
- `_capas/` — miniaturas usadas no índice.

Para gerar as páginas de uma revisão de novo: `cd revN && python _src/build.py` (a rev2 precisa de `pip install pillow pyyaml markdown`).

Para ver localmente: `python -m http.server 8000` e abrir http://localhost:8000
