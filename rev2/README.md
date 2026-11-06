# Cia. de Rafting — rev2

Versão com várias páginas, fiel ao site original do Wix (faixa azul com listras pinceladas e mascote, menu com submenus, títulos azuis espaçados, rodapé com o mascote), modernizada e responsiva, com painel de edição.

- Conteúdo editável: `_conteudo/site.yml` e `_conteudo/paginas/*.yaml` (um arquivo por página, feito de blocos).
- Gerador: `_src/build.py` (`pip install pillow pyyaml markdown`, depois `python _src/build.py` dentro desta pasta).
- Painel de edição e publicação automática: ver **GUIA-DE-EDICAO.md**.
- Para ver: `python -m http.server 8000` na pasta do projeto e abrir http://localhost:8000/rev2/
