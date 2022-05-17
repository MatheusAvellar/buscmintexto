import ast
import logging
import matplotlib.pyplot as plt
import statistics
import math

if __name__ == "__main__":
  logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

OUT_DIR = "../AVALIA/"

esperados = {}
esperados_votes = {}

f = plt.figure()
f.set_figwidth(8)
f.set_figheight(6)

logging.info(f"Lendo arquivo de 'esperados'")
with open("../RESULT/esperados.csv", "r") as esp_file:
  for line in esp_file:
    if line.startswith("QueryNumber"):
      continue
    # Adiciona na lista de 'esperados'
    qnum, dnum, dvotes = line.split(";")
    if qnum not in esperados:
      esperados[qnum] = []
      esperados_votes[qnum] = []

    # Cria uma lista com pseudo-ranking, e uma lista com os votos em si
    esperados[qnum].append([int(dnum), 5-int(dvotes)])
    esperados_votes[qnum].append([int(dnum), int(dvotes)])

for qnum in esperados:
  esperados[qnum].sort(key=lambda x: x[1])
  esperados_votes[qnum].sort(key=lambda x: -x[1])

def loginfo(stemmer, message):
  logging.info(f"{'NO' if not stemmer else ''}STEMMER: {str(message)}")

def getResults(stemmer):
  loginfo(stemmer, f"Lendo arquivo de 'resultados' ({'com' if stemmer else 'sem'} stemmer)")
  out = {}
  with open(f"../RESULT/resultados-{'NO' if not stemmer else ''}STEMMER.csv", "r") as res_file:
    for line in res_file:
      qnum, arr = line.split(";")
      # Pega os resultados da busca
      arr = ast.literal_eval(arr)
      # Para cada resultado
      for entry in arr:
        dnum = entry[1] or "err"
        dvotes = int(entry[0]) or -1
        # Adiciona na lista de 'encontrados'
        if qnum not in out:
          out[qnum] = []
        out[qnum].append([dnum, dvotes])
  return out

# Resultados da busca com e sem stemmer
encontrados_n = getResults(False)
encontrados_s = getResults(True)

logging.info("Resultados esperados e encontrados foram carregados com sucesso")

#-----
# Gráfico de 11 pontos de precisão e recall

def getRecPrec(stemmer, encontrados):
  rec_prec = {}

  for qnum in esperados:
    doc_esp = [e[0] for e in esperados[qnum]]
    doc_enc = [e[0] for e in encontrados[qnum]]
    rec_prec[qnum] = {}
    enc_so_far = []
    # Vamos 'descobrir' os resultados encontrados um a um
    for doc in doc_enc:
      # Adiciona cada doc novo encontrado na lista de encontrados
      enc_so_far.append(doc)
      # Calcula a interseção de relevantes e encontrados
      it_inters = list(set(doc_esp) & set(enc_so_far))
      # Calcula o recall e precision *até agora*
      new_rec = len(it_inters) / len(doc_esp)
      new_prec = len(it_inters) / len(enc_so_far)
      # Pegamos sempre a maior precisão para um dado recall
      # i.e. não registramos recalls repetidos
      if new_rec not in rec_prec[qnum]:
        rec_prec[qnum][new_rec] = new_prec

  loginfo(
    stemmer,
    "Recall/precision calculados. Exemplo para a consulta '00050':\n\t"
    + str(rec_prec["00050"])
  )
  return rec_prec

# Calcula recall e precision com e sem stemmer
rec_prec_n = getRecPrec(False, encontrados_n)
rec_prec_s = getRecPrec(True, encontrados_s)

logging.info("-"*8)

def get11pts(stemmer, rec_prec):
  _11pt = {}
  for qnum in rec_prec:
    _11pt[qnum] = {}
    # Cria lista de recalls (para comparar com %'s)
    recall_list = sorted(rec_prec[qnum].keys())
    # Para cada recall (em ordem decrescente)
    for rec in reversed(recall_list):
      # Itera sobre os 11 pontos (0%, 10%, ...)
      for pct in [n/10 for n in range(0, 10+1)]:
        if pct not in _11pt[qnum]:
          _11pt[qnum][pct] = -1
        # Se a porcentagem for menor ou igual ao recall
        if pct <= rec:
          # Salva a precision
          _11pt[qnum][pct] = rec_prec[qnum][rec]
    # Falta agora copiar a última precisão para as porcentagens finais
    # e.g. {... 0.8: 0.55, 0.9: 0,    1.0: 0    }
    #   -> {... 0.8: 0.55, 0.9: 0.55, 1.0: 0.55 }
    ref = 0.0
    for pct in _11pt[qnum]:
      last_pct = recall_list[-1]
      if pct > last_pct:
        ref = rec_prec[qnum][last_pct]

      if _11pt[qnum][pct] <= 0:
        _11pt[qnum][pct] = ref
      else:
        ref = _11pt[qnum][pct]

  loginfo(
    stemmer,
    "Gráfico de 11 pontos calculados. Exemplo para a consulta '00050':\n\t"
    + str(_11pt["00050"])
  )

  _11pt_avg = {}
  # Para cada porcentagem
  for pct in [n/10 for n in range(0, 10+1)]:
    # Calcula a média
    s = 0
    for qnum in _11pt:
      s += _11pt[qnum][pct]
    _11pt_avg[pct] = (s/len(_11pt))

  plt.title(
    "11 pontos de precisão/recall,\n"
    + f"média para todas as consultas ({'com' if stemmer else 'sem'} stemmer)")
  plt.ylim([0, 1])
  plt.xlim([0, 1])
  plt.plot([*_11pt_avg.keys()], [*_11pt_avg.values()], color=('red' if stemmer else 'blue'))
  plt.savefig(f"../AVALIA/11pontos-{'no' if not stemmer else ''}stemmer-1.png")
  plt.clf()
  loginfo(stemmer, "Um gráfico com a média dos 11 pontos foi criado")

# Calcula gráfico de 11 pontos com e sem stemmer
get11pts(False, rec_prec_n)
get11pts(True, rec_prec_s)

#-----
# F₁
## F₁ = 2PR / (P + R)
##    = 1/n (Σx F₁x)
##    = 1/n Σx (2PxRx)/(Px+Rx)

logging.info("-"*8)

def getF1(stemmer, rec_prec):
  f1 = 0
  for qnum in rec_prec:
    recall = max(rec_prec[qnum].keys())
    precision = rec_prec[qnum][recall]
    if recall + precision == 0:
      continue
    f1 += (2 * recall * precision) / (recall + precision)
  f1 /= len(rec_prec)

  loginfo(stemmer, f"F-score calculado para β=1:\n\tF1 = {f1} (≈{f1*100:.2f}%)")

  with open(f"../AVALIA/fscore-{'no' if not stemmer else ''}stemmer-2.txt", "w") as file:
    file.write(f"F1={f1}\n")

# Calcula F1 com e sem stemmer
getF1(False, rec_prec_n)
getF1(True, rec_prec_s)

#-----
# Precision@5

logging.info("-"*8)

def precisionAt(K, encontrados):
  precs = []
  for qnum in esperados:
    doc_esp = [e[0] for e in esperados[qnum]][:K]
    doc_enc = [e[0] for e in encontrados[qnum]][:K]
    inters = list(set(doc_esp) & set(doc_enc))
    precs.append([ qnum, len(inters) / K ])
  return precs

with open("../AVALIA/precision5-nostemmer-3.csv", "w") as file:
  file.write(f"QueryNumber;Precision@5\n")
  for prec in precisionAt(5, encontrados_n):
    qnum, p = prec
    file.write(f"{qnum};{p}\n")

with open("../AVALIA/precision5-stemmer-3.csv", "w") as file:
  file.write(f"QueryNumber;Precision@5\n")
  for prec in precisionAt(5, encontrados_s):
    qnum, p = prec
    file.write(f"{qnum};{p}\n")

logging.info("Precision@5 calculado; arquivos com os resultados foram criados")

#-----
# Precision@10

logging.info("-"*8)

with open("../AVALIA/precision10-nostemmer-4.csv", "w") as file:
  file.write(f"QueryNumber;Precision@10\n")
  for prec in precisionAt(10, encontrados_n):
    qnum, p = prec
    file.write(f"{qnum};{p}\n")

with open("../AVALIA/precision10-stemmer-4.csv", "w") as file:
  file.write(f"QueryNumber;Precision@10\n")
  for prec in precisionAt(10, encontrados_s):
    qnum, p = prec
    file.write(f"{qnum};{p}\n")

logging.info("Precision@10 calculado; arquivos com os resultados foram criados")

#-----
# Histograma de R-Precision (comparativo)

def getRPrecision(encontrados):
  out = []
  for qnum in esperados:
    doc_esp = [e[0] for e in esperados[qnum]]
    # Pega os 'R' primeiros resultados encontrados, onde 'R' é a quantidade de
    # documentos relevantes para a consulta
    doc_enc = [e[0] for e in encontrados[qnum]][:len(doc_esp)]
    inters = list(set(doc_esp) & set(doc_enc))
    out.append([ qnum, len(inters) / len(doc_esp) ])
  return out

rprec_n = getRPrecision(encontrados_n)
rprec_s = getRPrecision(encontrados_s)

rprec = []
for i in range(len(rprec_n)):
  rprec.append([
    # Número da consulta
    rprec_n[i][0],
    # Diferença entre NOSTEMMER e STEMMER
    rprec_n[i][1] - rprec_s[i][1]
  ])

# Imagem maior para caber o histograma
f.set_figwidth(15)
f.set_figheight(8)

plt.title("Histograma comparativo de R-Precision\n(+1 NOSTEMMER/−1 STEMMER)")
plt.ylim([-0.2, 0.2])
plt.xticks(rotation=90)
plt.set_loglevel("WARNING") # Evita mensagens chatas sobre datas
plt.bar([e[0] for e in rprec], [e[1] for e in rprec])
plt.savefig(f"../AVALIA/rprecision-7.png")
plt.clf()

# Volta ao tamanho padrão
f.set_figwidth(8)
f.set_figheight(6)

#-----
# MAP

logging.info("-"*8)

def getMAP(stemming, encontrados):
  avg_precisions = []
  for qnum in esperados:
    doc_esp = [e[0] for e in esperados[qnum]]
    doc_enc = [e[0] for e in encontrados[qnum]]
    enc_so_far = []
    precisions = []
    # Vamos 'descobrir' os resultados encontrados um a um
    for doc in doc_enc:
      # Adiciona cada doc novo encontrado na lista de encontrados
      enc_so_far.append(doc)
      # Se não é um documento relevante, pula pro próximo
      if doc not in doc_esp:
        continue
      # Calcula a interseção de relevantes e encontrados
      it_inters = list(set(doc_esp) & set(enc_so_far))
      # Calcula a precision *até agora*
      precisions.append(len(it_inters) / len(enc_so_far))
    avg_precisions.append(statistics.fmean(precisions))

  mean_avg_prec = statistics.fmean(avg_precisions)

  loginfo(stemming, f"MAP calculado:\n\tMAP = {mean_avg_prec} (≈{mean_avg_prec*100:.2f}%)")

  with open(f"../AVALIA/map-{'no' if not stemming else ''}stemmer-6.txt", "w") as file:
    file.write(f"MAP={mean_avg_prec}\n")

getMAP(False, encontrados_n)
getMAP(True, encontrados_s)

#-----
# MRR

logging.info("-"*8)

def getMRR(stemming, encontrados):
  mrr = 0
  for qnum in esperados:
    # Pega listas de documentos esperados e encontrados
    doc_esp = [e[0] for e in esperados[qnum]]
    doc_enc = [e[0] for e in encontrados[qnum]]
    # Encontra a posição do primeiro documento encontrado que é relevante
    k = 0
    for i in range(len(doc_enc)):
      if doc_enc[i] in doc_esp:
        k = i+1
        break
    # Soma o inverso da posição ao acumulador
    if k: mrr += 1/k
  mrr /= len(esperados)

  loginfo(stemming, f"MRR calculado:\n\tMRR = {mrr} (≈{mrr*100:.2f})")

  with open(f"../AVALIA/mrr-{'no' if not stemming else ''}stemmer-7.txt", "w") as file:
    file.write(f"MRR={mrr}\n")

getMRR(False, encontrados_n)
getMRR(True, encontrados_s)

#-----
# Discounted Cumulative Gain (médio)

logging.info("-"*8)

def getDCG(stemming, encontrados):
  dcg = {}
  # Para cada consulta
  for qnum in esperados:
    # Pega listas de documentos esperados e encontrados
    doc_esp = [e[0] for e in esperados[qnum]]
    doc_vot = [e[1] for e in esperados_votes[qnum]]
    # Corta os encontrados para limitar ao rank 10
    doc_enc = [e[0] for e in encontrados[qnum]][:10]

    i = 0
    gd = []
    for doc in doc_enc:
      i += 1
      # Encontra o index do documento na lista de esperados
      if doc in doc_esp:
        doc_i = doc_esp.index(doc)
        if doc_i >= 0:
          # Caso estejamos no primeiro caso
          if i == 1:
            # Pega a relevância diretamente
            gd.append(doc_vot[doc_i])
          else:
            # Caso contrário, divide pelo logaritmo
            gd.append(doc_vot[doc_i] / math.log2(i))
      else:
        # Se o documento não está na lista de esperados, relevância 0
        gd.append(0.0)

    # Cria a parte 'cumulativa' dos ganhos
    acc = 0
    dcg[qnum] = []
    for i in range(len(gd)):
      acc += gd[i]
      dcg[qnum].append(acc)

  # Calcula a média de cada um dos 10 resultados
  adcg = []
  for i in range(10):
    acc = 0
    for qnum in dcg:
      acc += dcg[qnum][i]
    adcg.append(acc / 10)

  plt.title(f"Média do Discounted Cumulative Gain\n{'no' if not stemming else ''}stemmer")
  plt.xlim([0, 10])
  plt.ylim([0, 80])
  plt.plot([*range(10)], adcg, color=('red' if stemming else 'blue'))
  plt.savefig(f"../AVALIA/dcg-{'no' if not stemming else ''}stemmer-8.png")
  plt.clf()
  loginfo(stemming, "Um gráfico com o DCG médio foi criado")

getDCG(False, encontrados_n)
getDCG(True, encontrados_s)
