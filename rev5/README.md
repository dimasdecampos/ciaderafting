# Cia. de Rafting — rev5 (sistema de páginas)

As 12 páginas do site original, com o mesmo conteúdo da rev2 (fiel ao Wix), num visual novo: claro, com a mesma paleta (azul, vermelho, amarelo), topo reorganizado e pensado primeiro para o celular.

- Ver: `python -m http.server 8000` na pasta do projeto e abrir http://localhost:8000/rev5/
- Gerar as páginas: `pip install pillow pyyaml markdown` e `python _src/build.py` (dentro de `rev5/`).
- Não editar os `.html` à mão: editar `_conteudo/` e gerar de novo.

## O topo

| Tela | O que aparece |
|---|---|
| Computador (acima de 1120 px) | barra fina com cidade, e-mail, WhatsApp e redes · cabeçalho branco fixo com logo, menu com submenus em painel e botão **Reservar** · listras da marca |
| Tablet (860–1120 px) | barra de contatos + logo, **Reservar** e **Menu** (gaveta lateral) |
| Celular | logo, botão do WhatsApp e menu; a gaveta abre com o grupo da página atual já aberto e traz contatos e redes no rodapé dela |

Toda página tem um **topo** claro: caminho (Home / grupo), título, subtítulo, botão de reserva (nas atividades) e a foto. A home usa o vídeo.

## Sistema de páginas

Cada página (`_conteudo/paginas/<nome>.yaml`) tem sempre a mesma forma:

```yaml
titulo_aba: ...          # título na aba do navegador / Google
descricao: ...           # descrição para o Google
topo:                    # topo da página
  titulo: ...
  subtitulo: ...
  imagem: foto.webp      # fotos ficam em assets/img/
  botoes: [...]          # opcional
secoes:                  # pilha de seções, de cima para baixo
  - fundo: branco        # branco | suave | azul
    sobretitulo: ...     # opcional (texto pequeno vermelho)
    titulo: ...          # opcional
    lado: {imagem, alt, posicao}   # opcional: figura ao lado (mascotes)
    blocos: [...]
```

Blocos disponíveis: `texto`, `destaque`, `titulo`, `sobretitulo`, `fatos`, `selos`, `caixa`, `botoes`, `galeria`, `etiquetas`, `barras`, `citacao`, `missao`, `ficha`, `preco`, `trilha`, `equipe`, `cartoes`, `numeros`, `imagem`, `colunas`, `formulario`. Caixas e trilhas seguidas viram uma grade automaticamente.

O menu fica em `_conteudo/site.yml` (com contatos, redes e textos do rodapé).

## Como isso vira WordPress

A estrutura foi feita para casar com o editor de blocos (Gutenberg), sem plugin:

| rev5 | WordPress |
|---|---|
| página `.yaml` | Página |
| `titulo_aba` / `descricao` | painel "Google e aba do navegador" (já existe no tema da rev4) |
| `topo.titulo` / `topo.subtitulo` / `topo.imagem` | Título / Resumo / Imagem destacada |
| seção (`fundo`, `titulo`) | bloco **Grupo** com estilo "Branco / Suave / Azul" + **Título** |
| `lado` | bloco **Mídia e texto** |
| `colunas` | bloco **Colunas** |
| `texto`, `destaque`, `citacao`, `titulo` | **Parágrafo**, Parágrafo estilo "Destaque", **Citação**, **Título** |
| `botoes` | **Botões** (estilos: azul, linha, WhatsApp) |
| `galeria`, `imagem` | **Galeria**, **Imagem** |
| `fatos`, `caixa`, `cartoes`, `trilha`, `equipe`, `numeros`, `preco`, `ficha`, `missao` | **padrões** (modelos prontos no "+") feitos de Grupo/Colunas com a classe do bloco |
| `menu` em `site.yml` | Aparência > Menus |
| CTA e rodapé | partes fixas do tema (dados em Personalizar) |

As classes do CSS (`sec--suave`, `alignwide`, `box`, `facts`, `cards`...) são as mesmas que os blocos/padrões vão usar, então `assets/css/style.css` pode ir direto para o tema.

## Arquivos

- `_src/build.py` — gerador.
- `_src/converte_rev2.py` — criou as páginas a partir da rev2 (cada título virou uma seção). Não sobrescreve páginas existentes.
- `assets/` — CSS, JS, fotos e vídeo (cópia da rev2).
