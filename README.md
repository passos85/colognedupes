# CologneDupes — site para GitHub Pages

Site estático (sem cookies, sem rastreio): 55 perfumes, páginas por perfume e por vibe, pesquisa, "perfume do dia", teste "Descobre o teu perfume", comunidade/comentários (Giscus), página de privacidade, 404, sitemap e robots.

## 1. Publicar (10 minutos)

1. Cria conta em github.com (se ainda não tiveres) e clica em **New repository**.
   - Nome: por exemplo `colognedupes` · Visibilidade: **Public** · não marques "Add a README".
2. Na página do repositório vazio, clica em **uploading an existing file** e arrasta **o conteúdo desta pasta** (não a pasta em si: o `index.html` tem de ficar na raiz do repositório). Inclui os ficheiros escondidos, em especial `.nojekyll`.
   - Se o navegador não deixar arrastar pastas, descompacta o ZIP e arrasta tudo de uma vez. Faz **Commit changes**.
3. Vai a **Settings → Pages**. Em *Build and deployment*: Source = **Deploy from a branch**, Branch = **main**, pasta **/ (root)** → **Save**.
4. Passado 1–2 minutos, o endereço aparece no topo da mesma página: `https://O-TEU-UTILIZADOR.github.io/colognedupes/`.

### Passo importante se usares o endereço github.io
Os ficheiros vêm preparados para `https://colognedupes.site`. Se usares outro endereço, ajusta o `sitemap.xml`, o `robots.txt` e as meta-tags de partilha:
- Edita `data/site.json` → campo `"url"` e corre `python3 tools/build.py` (ou `python3 tools/build.py --url https://O-TEU-UTILIZADOR.github.io/colognedupes`), depois volta a enviar os ficheiros alterados.
- Sem Python: faz "localizar e substituir" de `https://colognedupes.site` pelo teu endereço em todos os ficheiros (ex.: no VS Code, Ctrl+Shift+H).

## 2. Domínio próprio: colognedupes.site

1. Em **Settings → Pages → Custom domain** escreve `colognedupes.site` → Save. O ficheiro `CNAME` (com `colognedupes.site`) já vem incluído no pacote.
2. No painel do teu registador de domínios (DNS), cria:
   - 4 registos **A** para `@` (o domínio sem www): `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - 1 registo **CNAME** para `www` → `O-TEU-UTILIZADOR.github.io`
3. Quando o GitHub validar o DNS (pode demorar de minutos a 24 h), marca **Enforce HTTPS**. Recomendo não saltar este passo: sem HTTPS, os navegadores mostram o site como "não seguro".
   - Só deves usar o domínio depois de teres a certeza de que é teu no registador. O perfil do TikTok continua a ser `@colognedupes.pt` (é o nome do perfil, não do site).
4. Confirma que `data/site.json` tem `"url": "https://colognedupes.site"`.

## 3. Atualizar o "Último TikTok" (30 segundos)

Edita `data/site.json` no GitHub (lápis → Commit):

```json
"tiktok": {
  "perfil": "https://www.tiktok.com/@colognedupes.pt",
  "titulo": "5 perfumes por menos de €30",
  "data": "16/11/2026",
  "video": "https://www.tiktok.com/@colognedupes.pt/video/1234567890123456789"
}
```
Com `video` preenchido aparece o botão "Ver aqui" (o vídeo só carrega quando a pessoa clica). Sem `video`, o botão abre o teu perfil. Depois corre `python3 tools/build.py` e envia os ficheiros alterados (a página inicial é gerada a partir daqui).

## 4. Comunidade e comentários (Giscus)

O site antigo usava uma base de dados que só funciona dentro do claude.ai; aqui usamos o **Giscus**, que guarda os comentários nas *Discussions* do teu repositório. Enquanto não estiver configurado, as páginas mostram "Os comentários vão abrir em breve".

1. No repositório: **Settings → General → Features → Discussions** (ligar).
2. Em **Discussions**, cria uma categoria "Comentarios" do tipo *Announcement* (só tu crias tópicos; as pessoas comentam).
3. Instala a app em github.com/apps/giscus (só neste repositório).
4. Vai a giscus.app, escreve `utilizador/repositorio`, escolhe a categoria e copia `data-repo-id` e `data-category-id`.
5. Preenche em `data/site.json`:
```json
"giscus": { "repo": "utilizador/colognedupes", "repoId": "R_...", "categoria": "Comentarios", "categoriaId": "DIC_..." }
```
6. Corre `python3 tools/build.py` e envia os ficheiros. Quem quiser comentar precisa de conta GitHub; modera apagando comentários nas Discussions.

## 5. Adicionar ou corrigir perfumes (só no navegador, sem instalar nada)

O site é gerado a partir de `data/perfumes.json`. Com o ficheiro `.github/workflows/static.yml` deste pacote no repositório, **basta editares esse ficheiro no GitHub**: o próprio GitHub gera as páginas e publica o site em 2 a 3 minutos.

### Preparação (uma vez só)
1. Em **Settings → Pages**, em *Build and deployment*, a fonte (Source) tem de ser **GitHub Actions**.
2. No repositório abre `.github/workflows/static.yml`, clica no **lápis**, apaga tudo e cola o conteúdo do ficheiro `static.yml` deste pacote. Faz **Commit changes**. Esse ficheiro passa a gerar as páginas e a publicar o site de cada vez que alteras alguma coisa.
3. Envia o resto da atualização (pastas `perfumes`, `vibe`, `data`, `tools` e `sitemap.xml`) com **Add file → Upload files**.

### Adicionar um perfume
1. No repositório abre `data/perfumes.json` e clica no **lápis** (Edit).
2. Vai ao fim do ficheiro: o último perfume termina com `}` e depois vem `]`. Acrescenta uma vírgula a seguir ao último `}` e cola por baixo o bloco novo (modelo abaixo).
3. Clica em **Commit changes**.
4. Abre o separador **Actions**: aparece "Publicar site" a correr. Quando ficar com um visto verde, o site atualiza em 1 a 2 minutos. Se ficar com uma cruz vermelha, abre-o: a mensagem "ERRO:" diz o que corrigir (vírgula em falta, id repetido, tag inexistente) e o site antigo continua online.

Modelo (copia, muda os valores e mantém as aspas e as vírgulas):

```json
{
 "id": "nomesemespacos",
 "marca": "LATTAFA",
 "nome": "NOME DO PERFUME",
 "notas": ["Baunilha", "Âmbar", "Caramelo", "Almíscar"],
 "tags": ["doce", "noite"],
 "ocasioes": ["noite", "date"],
 "estacao": "outono e inverno",
 "descricao": "Uma ou duas frases sobre o cheiro, sem comparar com marcas.",
 "piramide": null,
 "verificado": false
}
```

- `id`: único, só letras minúsculas sem acentos e números, sem espaços.
- `tags` válidas: `doce fresco especiado noite trabalho date dia`.
- `ocasioes` válidas: `noite date festa dia trabalho`.
- `estacao`: por exemplo `todo o ano`, `outono e inverno`, `primavera e verão`.
- `verificado`: `false` mostra o aviso de "notas aproximadas". Põe `true` só quando confirmares as notas.
- Para corrigir um perfume, edita o bloco dele no mesmo ficheiro. Para apagar, remove o bloco todo (e a vírgula que sobrar).

### Sem Actions (alternativa)
Corre `python3 tools/build.py` no teu computador (precisa só de Python 3) e envia para o GitHub os ficheiros alterados: **Add file → Upload files**, arrastando as pastas `perfumes`, `vibe` e os ficheiros `data/perfumes.json` e `sitemap.xml`.

## 6. Notas legais e boas práticas

- O site não tem preços nem "igual a [marca]": descreve notas, vibe e ocasião. Mantém assim.
- Preenche `"contacto"` em `data/site.json` com um email de contacto (aparece na página de privacidade).
- A página `/privacidade/` é um texto-base; não substitui aconselhamento jurídico.
- Fontes (Cormorant Garamond e Montserrat) alojadas no próprio site, com licença OFL em `assets/fonts/`.
