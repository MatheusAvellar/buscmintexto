import re
import nltk
import math
import time
import string
import logging

if __name__ == "__main__":
  logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

STEMMER = False
MODELO = ""
CONSULTAS = ""
RESULTADOS = ""

# Lê o arquivo de configuração, pega nomes de arquivos a serem lidos/criados
with open("../BUSCA.CFG", "r") as config_file:
  logging.info("Arquivo de configuração aberto")
  for line in config_file:
    if line.startswith("STEMMER"):
      # Se encontra STEMMER, liga a flag
      # Caso contrário, assume que NOSTEMMER está presente
      STEMMER = True
    elif line.startswith("MODELO="):
      MODELO = line[7:].strip()
      logging.info(f"Configuração 'MODELO': '{MODELO}'")
    elif line.startswith("CONSULTAS="):
      CONSULTAS = line[10:].strip()
      logging.info(f"Configuração 'CONSULTAS': '{CONSULTAS}'")
    elif line.startswith("RESULTADOS="):
      RESULTADOS = line[11:].strip()
      logging.info(f"Configuração 'RESULTADOS': '{RESULTADOS}'")

doc_ids = None
matrix = {}

logging.info(f"Lendo arquivo de MODELO")
with open(MODELO, "r") as model_file:
  it = 0
  for line in model_file:
    # Primeira linha contém os IDs de documentos
    if not it:
      it += 1
      doc_ids = list(map(int, line.split(";")))
      continue
    # Outras linhas contém TERMO;(lista de tf-idf em cada documento)
    term, *tfidf = line.split(";")
    # Cria a entrada na matriz de pesos com tf-idf's correspondentes ao termo
    matrix[term] = list(map(float, tfidf))
    it += 1

  logging.info(f"Lidas '{it}' linhas de MODELO")


queries = {}

logging.info(f"Lendo arquivo de CONSULTAS")
with open(CONSULTAS, "r") as query_file:
  it = 0
  for line in query_file:
    # Cabeçalho não entra na história
    if not it:
      it += 1
      continue
    it += 1
    # Quebra linha em número da consulta e texto
    query_num, text = line.split(";")
    # Tokenização
    nltk_tokens = nltk.word_tokenize(text)
    # Remove pontuação
    # [Ref] https://stackoverflow.com/a/38734861/4824627
    tokens = [x for x in nltk_tokens if not re.fullmatch('[' + string.punctuation + ']+', x)]
    queries[query_num] = tokens

  logging.info(f"Lidas '{it}' linhas de CONSULTAS")

# Similaridade entre consulta e documento
# (Q · D[i]) / (|Q|*|D[i]|)
def sim(query, doc_index):
  ## Numerador: Q · D[i] = Σ w[Q,j] w[i,j]
  ## Somatório do produto entre os pesos da consulta
  ## com os pesos do documento
  ## Toda palavra na consulta tem peso 1
  ## Então, queremos o somatório dos pesos (tfidf) do
  ## documento das palavras que aparecem na consulta
  # Pega o index do documento
  w = 0
  # Soma o peso dos termos da consulta no documento
  for word in query:
    if word in matrix:
      w += matrix[word][doc_index]
  ## Denominador: |Q|*|D[i]| = √Σw²
  ## Raiz do somatório dos quadrados dos pesos
  ## de todas as palavras do documento
  D = 0
  for word in matrix:
    D += matrix[word][doc_index]**2
  # O somatório da consulta, como só possui peso 1,
  # é somente o número de palavras
  d = math.sqrt(len(query)) * math.sqrt(D)

  return w/d


ranking = {}

logging.info(f"Calculando similaridades")
start_all = time.process_time()
for query_num in queries:
  start_q = time.process_time()
  ranking[query_num] = []
  for i in range(len(doc_ids)):
    s = sim(queries[query_num], i)
    ranking[query_num].append([0, doc_ids[i], s])

  # Ordena por similaridade descendente (maior primeiro)
  ranking[query_num].sort(key=lambda x: x[2], reverse=True)
  for i in range(len(ranking[query_num])):
    ranking[query_num][i][0] = i+1

  logging.info(f"Consulta '{query_num}' levou {time.process_time() - start_q:.4f} segundos")

total_time = (time.process_time() - start_all) / 60
logging.info(f"Cálculo de todas as similaridades levou {total_time:.4f} minutos")

_out_ = RESULTADOS.rpartition(".")
_out_filext = _out_[-1] or "csv"
_out_filename = f"{_out_[0]}-{'STEMMER' if STEMMER else 'NOSTEMMER'}.{_out_filext}"
logging.info(f"Escrevendo no arquivo de RESULTADOS, '{_out_filename}'")
with open(_out_filename, "w") as file:
  for query_num in queries:
    file.write(f"{query_num};{ranking[query_num]}\n")
