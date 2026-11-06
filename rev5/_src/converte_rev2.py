"""Converte as páginas da rev2 (lista de blocos) para o formato da rev5 (topo + seções).

Uso (a partir da pasta rev5):  python _src/converte_rev2.py
Rodado uma vez para criar _conteudo/paginas/*.yaml com o mesmo conteúdo da rev2.
Não sobrescreve páginas que já existem (apague o arquivo para gerar de novo).

Regras:
- o primeiro bloco "cabecalho" vira o topo da página (título e subtítulo);
- a foto de "banner" vira a imagem do topo;
- cada bloco "titulo" abre uma seção nova, com o título da seção;
- as seções alternam o fundo (branco / suave);
- a imagem "lateral" (mascotes) vai para o lado da primeira seção.
"""
import os
import yaml

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
REV2 = os.path.join(os.path.dirname(ROOT), "rev2", "_conteudo", "paginas")
OUT = os.path.join(ROOT, "_conteudo", "paginas")


def nome_img(ref):
    return os.path.basename(str(ref or "")) or None


def limpa_imagens(obj):
    """Troca '/rev2/assets/img/foto.webp' por 'foto.webp' em qualquer lugar."""
    if isinstance(obj, dict):
        return {k: (nome_img(v) if k in ("imagem", "foto") and v else limpa_imagens(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [limpa_imagens(i) for i in obj]
    return obj


def converte(slug, d):
    d = limpa_imagens(d)
    blocos = [b for b in (d.get("blocos") or []) if b]
    topo = {}
    for i, b in enumerate(blocos):
        if b.get("tipo") == "cabecalho":
            topo["titulo"] = b.get("titulo")
            if b.get("subtitulo"):
                topo["subtitulo"] = b["subtitulo"]
            blocos.pop(i)
            break
    foto = d.get("banner") or d.get("hero") or {}
    if not foto.get("imagem"):  # página sem banner: usa a primeira foto da galeria
        for b in blocos:
            if b.get("tipo") == "galeria" and b.get("fotos"):
                foto = b["fotos"][0]
                break
    if foto.get("imagem"):
        topo["imagem"] = foto["imagem"]
        topo["alt"] = foto.get("alt", "")

    secoes, atual = [], {"blocos": []}
    for b in blocos:
        if b.get("tipo") == "titulo":
            if atual["blocos"] or atual.get("titulo"):
                secoes.append(atual)
            atual = {"titulo": b.get("titulo"), "blocos": []}
            if b.get("ancora"):
                atual["ancora"] = b["ancora"]
            continue
        atual["blocos"].append(b)
    if atual["blocos"] or atual.get("titulo"):
        secoes.append(atual)

    lateral = d.get("lateral") or {}
    if lateral.get("imagem") and secoes:
        secoes[0]["lado"] = {"imagem": lateral["imagem"], "alt": lateral.get("alt", ""),
                             "posicao": lateral.get("posicao", "direita")}

    out = []
    for n, s in enumerate(secoes):
        sec = {"fundo": "branco" if n % 2 == 0 else "suave"}
        sec.update(s)
        out.append(sec)
    return {"titulo_aba": d.get("titulo_aba"), "descricao": d.get("descricao"), "topo": topo, "secoes": out}


class Dumper(yaml.SafeDumper):
    pass


def _str(dumper, s):
    style = "|" if "\n" in s else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", s, style=style)


Dumper.add_representer(str, _str)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in sorted(os.listdir(REV2)):
        if not f.endswith((".yml", ".yaml")):
            continue
        dest = os.path.join(OUT, f)
        if os.path.exists(dest):
            print("já existe, mantido:", f)
            continue
        d = yaml.safe_load(open(os.path.join(REV2, f), encoding="utf-8")) or {}
        novo = converte(os.path.splitext(f)[0], d)
        with open(dest, "w", encoding="utf-8", newline="\n") as fh:
            yaml.dump(novo, fh, Dumper=Dumper, allow_unicode=True, sort_keys=False, width=1000)
        print("ok", f)
