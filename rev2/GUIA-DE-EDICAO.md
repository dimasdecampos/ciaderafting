# Guia de edição do site (rev2)

O site é editado por um painel na internet (Pages CMS). Cada alteração salva vira uma atualização do site, que fica no ar em cerca de **1 a 2 minutos**. Todo o histórico fica guardado: se algo der errado, dá para voltar atrás.

## Ativar o painel (uma vez só — quem administra o repositório)

1. **Mudar a forma de publicação do GitHub Pages** (obrigatório, antes do primeiro envio):
   GitHub → repositório `ciaderafting` → *Settings* → *Pages* → em *Build and deployment*, escolher **Source: GitHub Actions**.
2. **Enviar os arquivos novos para o GitHub** (`.pages.yml`, `.github/workflows/publicar.yml`, pasta `rev2/_conteudo` e as alterações em `rev2/_src` e `rev2/assets`). A partir daí, cada envio publica o site sozinho (aba *Actions* mostra o andamento).
3. **Abrir o painel**: acessar https://app.pagescms.org, entrar com a conta do GitHub, instalar o app do Pages CMS no repositório `ciaderafting` e abrir o projeto.
4. **Dar acesso ao cliente**: no GitHub, *Settings* → *Collaborators* → convidar a conta dele com permissão de escrita. Ele entra no mesmo endereço do painel.

## Como o cliente edita

- **Páginas**: abrir a página desejada. No alto ficam o título da aba, a descrição para o Google e as fotos de topo. Abaixo, a lista de **blocos** (textos, títulos, quadros de informação, galerias, botões...). Cada bloco pode ser editado, **reordenado** (arrastando), **removido** ou **adicionado** pelo botão de adicionar.
- **Fotos**: ao escolher ou enviar uma foto, pode ser direto do celular (jpg ou png). O site reduz e converte sozinho. Sempre preencher a "descrição da foto".
- **Dados gerais do site**: telefone, e-mail, redes sociais, mensagens do WhatsApp e rodapé, num lugar só.
- Para **salvar**, usar o botão *Save*. Depois de 1 a 2 minutos a mudança aparece no site.

### Combinados

- Não criar nem excluir páginas pelo painel (o menu do site é fixo). Para uma página nova, falar com quem mantém o site.
- Não mudar o nome interno dos arquivos.
- O painel edita o conteúdo, não o desenho do site (cores, fontes, posição do menu).

## Se algo não aparecer

1. Conferir no GitHub, aba **Actions**, se a última publicação ficou verde. Se ficou vermelha, abrir o registro e ler o erro (geralmente um arquivo de foto com problema).
2. O registro também mostra linhas "AVISO: imagem não encontrada" quando uma foto referenciada não existe.

## Para quem mantém o código

- Conteúdo: `rev2/_conteudo/site.yml` e `rev2/_conteudo/paginas/*.yml`. Formato dos blocos: `rev2/_src/build.py` (funções `b_*`) e telas do painel: `.pages.yml` (precisam andar juntos).
- Gerar as páginas localmente: `pip install pillow pyyaml markdown` e `python rev2/_src/build.py`.
- Os `.html` da rev2 que estão no repositório são regenerados a cada publicação; não editar à mão.
- Fotos enviadas em jpg/png são convertidas para `rev2/assets/img/auto/` (não vai para o Git; é gerado na publicação).
