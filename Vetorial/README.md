O programa é executado pelos comandos a seguir, na ordem em que são apresentados
abaixo, dentro da pasta `SRC/`.

Um exemplo do output retornado ao executar cada um dos comandos está disponível
em `output.txt`.

```bash
python processador-de-consultas.py
```

Lê o arquivo `data/cfquery.xml`.

Gera os arquivos `consultas.csv` (≈10 KB) e `esperados.csv` (≈60 KB) em `RESULT/`.

---

```bash
python gerador-lista-invertida.py
```

Lê os arquivos `data/cf74.xml` a `data/cf79.xml`.

Gera o arquivo `lista-invertida.csv` (<1 MB).

---

```bash
python indexador.py
```

Lê o arquivo `lista-invertida.csv`.

Gera o arquivo `tfidf.csv` (≈45 MB).

Demora ≈10 segundos.

---

```bash
python buscador.py
```

Lê os arquivos `tfidf.csv`, `consultas.csv` e `resultados.csv`.

Gera um arquivo `resultados-STEMMER.csv` ou `resultados-NOSTEMMER.csv` (≈4 MB),
dependendo da configuração.

Demora ≈4 minutos. Este é o script mais
demorado, pois precisa calcular a similaridade entre todas as consultas e todos
os documentos.

O cálculo de similaridade de cada consulta, sem stemming, leva entre 2 e 3
segundos para ser realizado; com stemming, leva entre 1 e 2 segundos.

---

```bash
python avaliador.py
```