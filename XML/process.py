#!/usr/bin/python

# 1. Obter todos os AUTHOR em cf79.xml
# Usando ElementTree XML API
# https://docs.python.org/3/library/xml.etree.elementtree.html
import xml.etree.ElementTree as ET

a_count = 0
root = ET.parse("cf79.xml").getroot()
with open("autores.xml", "w") as file:
  # Para toda tag <AUTHOR>
  for author in root.iter("AUTHOR"):
    # Pega seu conteúdo textual
    text = author.text
    # Escreve no arquivo (com \n removidos)
    text = text.replace('\n', ' ')
    file.write(f"{text}\n")
    a_count += 1

print(f"Encontrados {a_count} autores via ")

# 2. Obter todos os TITLE em cf79.xml
# Usando Document Object Model API
# https://docs.python.org/3.8/library/xml.dom.html
import xml.dom.minidom as dom

t_count = 0
document = dom.parse("cf79.xml").documentElement
with open("titulo.xml", "w") as file:
  # Para toda tag <TITLE>
  for title in document.getElementsByTagName("TITLE"):
    # Pega seu conteúdo textual
    text = title.firstChild.nodeValue
    # Escreve no arquivo (com \n removidos)
    text = text.replace('\n', ' ')
    file.write(f"{text}\n")
    t_count += 1

print(f"Encontrados {t_count} títulos")
print(f"Média de {a_count/t_count:.2f} autores por artigo")