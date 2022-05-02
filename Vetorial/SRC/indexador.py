import re
import math
import logging
import time
from collections import Counter

if __name__ == "__main__":
  logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

LEIA = ""
ESCREVA = ""

# Lê o arquivo de configuração, pega nomes de arquivos a serem lidos/criados
with open("../INDEX.CFG", "r") as config_file:
  logging.info("Arquivo de configuração aberto")
  for line in config_file:
    if line.startswith("LEIA="):
      LEIA = line[5:].strip()
      logging.info(f"Configuração 'LEIA': '{LEIA}'")
    elif line.startswith("ESCREVA="):
      ESCREVA = line[8:].strip()
      logging.info(f"Configuração 'ESCREVA': '{ESCREVA}'")

# Dicionário de termos vs documentos a ser recuperado do arquivo
td = {}
not_AZ_regex = re.compile(r"[^A-Z]")
line_count = 0
# Abre arquivo de lista invertida
with open(LEIA, "r") as data_file:
  for line in data_file:
    line_count += 1
    # Separa termo e documentos
    term, docs = line.split(";")

    # Regras:
    # - Apenas palavras com 2 letras ou mais
    if len(term) < 2: continue
    # - Apenas palavras com apenas letras (maiúsculas)
    if not_AZ_regex.search(term): continue

    # Converte lista texto para lista de ints em Python
    # Remove espaços, '[' e ']', quebra em ", ", mapeia
    # para ints, e retorna como lista:
    #                   docs.strip()[1:-1]               
    #                                     .split(", ")   
    #           map(int,                               ) 
    #      list(                                        )
    docs = list(map(int, docs.strip()[1:-1].split(", ")))
    # Coloca a lista em memória
    td[term] = docs

logging.info(f"Encontradas {len(td)} palavras válidas de um total de {line_count} ({(len(td)/line_count)*100:.2f}%)")

# Faz a agregação de todos os IDs de documentos mencionados
all_doc_num = []
# Conta o tamanho de cada documento, em # de palavras
docsize = {}
for term in td:
  # Concatena lista de documentos do termo com a agregada
  all_doc_num += td[term]
  # Atualiza o tamanho de cada documento mencionado
  for doc in td[term]:
    if doc not in docsize:
      docsize[doc] = 0
    docsize[doc] += 1
# Cria uma lista ordenada documentos *distintos* mencionados
docset = sorted(set(all_doc_num))
# Número total de documentos distintos
N = len(docset)
logging.info(f"Número total de documentos distintos: '{N}'")

n = {}
td_count = {}
for term in td:
  # Conta documentos distintos que contém o termo
  n[term] = len(set(td[term]))
  # Conta ocorrências em documentos
  # e.g. td_count['FET'] => Counter({ 1220: 3 })
  # i.e. 'FET' aparece 3 vezes no documento 1220
  td_count[term] = Counter(td[term])

# tfn(i,j) = tf[ij] / max[k](tf[ij])
def tf(doc, term):
  # Se esse termo não está no documento, retorna 0
  if term not in td_count or doc not in td_count[term]:
    return 0
  # Caso contrário, retorna o número de ocorrências
  return td_count[term][doc] / docsize[doc]

# idf[j] = log(N/n[j])
def idf(term):
  return math.log10( N / n[term] )

# tf-idf = tf * idf
def tfidf(doc, term):
  return tf(doc, term) * idf(term)

logging.info("Teste da função de TF:"
  + f"\n\tTermo 'THE', doc  #333:  {tf(333, 'THE'):.4f} (freq.)"
  + f"\n\tTermo 'FET', doc #1220:  {tf(1220, 'FET'):.4f} (infreq.)")
logging.info("Teste da função de IDF:"
  + f"\n\tTermo 'THE':  {idf('THE'):.4f} (freq.)"
  + f"\n\tTermo 'FET':  {idf('FET'):.4f} (infreq.)")
logging.info("Teste da função de TF-IDF:"
  + f"\n\tTermo 'THE', doc  #333:  {tfidf(333, 'THE'):.4f} (freq.)"
  + f"\n\tTermo 'THE', doc #1220:  {tfidf(1220, 'THE'):.4f} (infreq.)"
  + f"\n\tTermo 'FET', doc  #333:  {tfidf(333, 'FET'):.4f} (infreq.)"
  + f"\n\tTermo 'FET', doc #1220:  {tfidf(1220, 'FET'):.4f} (freq.)")

logging.info(f"Escrevendo matriz de documentos/tf-idf")
start = time.process_time()
with open(ESCREVA, "w") as file:
  # Escreve lista de IDs de documentos
  file.write(f"{';'.join(map(str, docset))}\n")
  # Escreve uma linha no arquivo para cada termo,
  # com o tf-idf para cada documento
  out = []
  for term in list(td.keys()):
    out.append(term)
    for doc in docset:
      out.append(tfidf(doc, term))
    file.write(f"{';'.join(map(str, out))}\n")
    out.clear()

logging.info(f"Levou {time.process_time() - start:.4f} segundos")
