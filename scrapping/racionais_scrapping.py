# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 09:51:16 2019

@author: Celso Pereira Neto


"""
import datetime as dt
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
start = dt.datetime.now()

class InfoLetra:
    """ Objeto que faz o webscrapping, recolhe titulo e letra.
    """

    def __init__(self, link_letra):
        """
            Recolhe as informações sobre a letra da música a partir do link.
            titulo e letra
            Inicia __status_dataframe para o backcheck
        """
        self.__bs_letra = BeautifulSoup(requests.get(link_letra).content,
                                        'html.parser')
        self.__titulo = self.__bs_letra.find("h1", "head-title").string
        self.__letra_finds = self.__bs_letra\
        .find("div", class_="lyric-original").find_all('p')

    def titulo(self):
        """
            Retorna o título da música.
        """
        return str(self.__titulo)


    def letra(self):
        """
            retorna a letra substituindo formatação.
        """
        para_remover = ["<br/>",
                        "</br>",
                        "<br>",
                        "[",
                        "]",
                        "'"
                        ]
        letra_em_lista = [find.contents for find in self.__letra_finds]
        letra = ''.join(map(str, letra_em_lista))
 
        for char in para_remover:
            letra = letra.replace(char, " ")
        para_trocar = [" ,", ",,", ", , "]
 
        for char in para_trocar:
            letra = letra.replace(char, ",")

        return  letra

    def reseta_titulo(self, novo_titulo):
        """
            Muda o título da música conforme desejado.
            Utiizado para facilitar o fuzzy matching das músicas no site com
            a tabela da wikipedia.
        """
        self.__titulo = novo_titulo


def recupera_letra(row, a_infos_letras):
    """
        Adiciona ao DataFrame da Wikipedia as letras obtidas.

          A busca fuzzy pelo titulo ajuda a econtrar diversos titulos que
        possuem  diferenças sutis, porém há dificuldade no álbum
        cores & valores e nas músicas vida loka pt 1, 2 e intro.
          VÁRIAS tentativas e erros para identificar e tratar os titulos
        divergentes no arquivo configs.
    """
    row['titulo_encontrado'] = ''
    row['letra'] = ''
    row['metodo'] = ''
    row['ratio'] = 0
    if row['Álbum'] == "Cores & Valores":
        row['Canção'] = row['Canção'].replace("&", "e").replace(":", "")

    for info_letra in a_infos_letras:
        if info_letra.titulo() == row['Canção']:
            row['titulo_encontrado'] = info_letra.titulo()
            row['letra'] = info_letra.letra()
            row['metodo'] = 'igualdade'
            row['ratio'] = fuzz.ratio(info_letra.titulo(), row['Canção'])
        elif fuzz.ratio(info_letra.titulo(), row['Canção']) > 80 and \
        row['letra'] == '':
            row['titulo_encontrado'] = info_letra.titulo()
            row['letra'] = info_letra.letra()
            row['metodo'] = 'fuzzy'
            row['ratio'] = fuzz.ratio(info_letra.titulo(), row['Canção'])

    return row

def arruma_albums(row):
    album = row['Álbum']
    for item in configs["albums_rm"]:
        album =  album.replace(item, '')
        album = album.strip()
        if album in ['', 'Nenhum']:
            album = 'singles'
        if album == 'Escolha seu Caminho':
            album = 'Escolha o seu Caminho'
    row['Álbum'] = album
    return row

with open("configs.json", encoding='utf-8') as file:
    configs = json.load(file)

MENU_LETRAS = BeautifulSoup(requests.get(configs['MENU_LETRAS']).content,
                            'html.parser')
WIKI = BeautifulSoup(requests.get(configs['WIKIPAGE']).content, 'html.parser')
TABELA_WIKI = WIKI.find("table", "wikitable")
links_letras = MENU_LETRAS.find(id='cnt-artist-songlist').find_all('a')

links_letras = MENU_LETRAS.find(id='cnt-artist-songlist').find_all('a',class_='songList-table-songName')

with open("index.html", encoding='utf-8') as html_file:
    HTML = html_file.read()

tabela_html = BeautifulSoup(HTML, 'html.parser')
tabela_html.body.append(TABELA_WIKI)

# necessidade do [0]
# pd.read_html() retorna uma lista de DataFrames
songs_wiki_df = pd.read_html(str(tabela_html))[0]
songs_wiki_df = songs_wiki_df.apply(arruma_albums, axis=1)
links_d = {}
for i, link  in enumerate(links_letras):
    links_d[i] = configs['HOME_PAGE'] + link.get('href')

falsas_conhecidas = configs['falsas_conhecidas']
erradas_conhecidas = configs['dict_erradas']
infos_letras = []

for (i, item) in enumerate(links_d.items()):
    infos_letras.append(InfoLetra(item[1]))
    titulo = infos_letras[i].titulo()
    if titulo in configs['dict_erradas'].keys():
        infos_letras[i].reseta_titulo(configs['dict_erradas'][titulo])

infos_letras = [song for song in infos_letras if song.titulo() \
              not in falsas_conhecidas]


# Separando as instrumentais e outros casos especiais,
songs_wiki_letras = songs_wiki_df.loc[~songs_wiki_df['Canção']\
                                  .isin(configs["instrumentais_misc"])]
songs_wiki_letras = songs_wiki_letras.apply(lambda x: recupera_letra(x, infos_letras),
                                            axis=1)

result = songs_wiki_letras.append(songs_wiki_df.loc[songs_wiki_df['Canção']\
                                  .isin(configs["instrumentais_misc"])],\
                                  sort=False)

with open('data.json', 'w', encoding='utf-8') as file:
    result.to_json(file, force_ascii=False)
end = dt.datetime.now()
time = end - start
print("A extração demorou {} segundos.".format(time.seconds))
