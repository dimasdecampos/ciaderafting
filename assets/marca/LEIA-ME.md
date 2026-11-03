# Logo vetorizado — Cia. de Rafting

Vetorizado a partir do logo original do site antigo (`logo-original.png`, 2336 × 1023 px).

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `logo-cia-de-rafting.svg` | Vetor, texto escuro. Para fundos claros, impressão e gráficas. |
| `logo-cia-de-rafting-branco.svg` | Vetor, texto branco. Para fundos escuros e sobre fotos. |
| `logo-cia-de-rafting-camadas.svg` | Vetor em camadas, usado no site para animar. O texto usa `currentColor` (assume a cor do texto ao redor). |
| `logo-cia-de-rafting.png` | PNG transparente 2336 × 1023, texto escuro. |
| `logo-cia-de-rafting-branco.png` | PNG transparente 2336 × 1023, texto branco. |
| `logo-original.png` | Arquivo raster original, como referência. |

## Camadas do SVG

- `lg-p--blue`: faixa azul
- `lg-p--yellow`: remo amarelo
- `lg-p--red`: remo vermelho
- `lg-text`: letras. Cada letra é um elemento `lg-l` separado, numerado da esquerda para a direita pela variável `--i`.

## Cores

| Cor | Hex |
|---|---|
| Vermelho | `#ed3237` |
| Amarelo | `#fef112` |
| Azul | `#2b5687` |
| Texto | `#232121` |

As cores foram medidas no arquivo original. Se a marca tiver uma especificação oficial (Pantone ou CMYK), ela tem prioridade.

## Como refazer a vetorização

O script está em `_src/logo-src/trace_logo.py` e precisa de `numpy`, `pillow` e `potracer`.
