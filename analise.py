#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 16:24:24 2019

@author: Celso Pereira Neto
"""
import os
import pandas as pd
import spacy

nlp = spacy.load("pt_core_news_sm")

pd.options.display.max_rows = 100
pd.options.display.max_columns = 50
caminho_arquivo = "scrapping" + os.sep + "data.json"
df = pd.read_json(caminho_arquivo, encoding='utf-8')
df = df[['Canção', 'Participantes', 'Álbum', 'letra']]

df['Participantes'] = df.apply(lambda x:
    [el.strip() for el in x['Participantes'].split(",")], axis=1)


# verificar os participantes listados:
# para depois analisar a participação
# testar o get_dummies()

#de np.ndarray para list
listed = list(df['Participantes'].values)
# essa compreensão de lista confesso que devo ao stackoverflow :D
# flat_list = [item for sublist in l for item in sublist]
total_participantes = [nome for nomes in listed for nome in nomes]
# provavelmente não vai ser útil se precisarmos da ordem

participantes_unique = list(set(total_participantes)) 

df_letras = df.loc[~df['letra'].isnull()].copy().reset_index(drop=True)


class NlpLetra:
    """
        Objeto que busca no modulo spaCy a interpretaçao da letra.
    """
    def __init__(self, letra):
        self.__nlp = nlp(letra)
        self.__excluir = ["SPACE", "PUNCT"]
        self.__pos_dict()
        

    def texts(self):
        return [token.text for token in self.__nlp \
                if token.pos_ not in self.__excluir]

    def pospeech(self):
        return [token.pos_ for token in self.__nlp\
                if token.pos_ not in self.__excluir]


    def tags(self):
        return [token.tag_ for token in self.__nlp\
                if token.pos_ not in self.__excluir]
        
    def __pos_dict(self):
        self.pos_dict =   {
         "pos": self.pospeech(),
         "tag": self.tags(),
         "text": self.texts()
         }
        
    def deps(self):
        return [token.dep_ for token in self.__nlp\
                if token.pos_ not in self.__excluir]

    def ents(self):
        return [(entity, entity.label_) for entity in self.__nlp.ents]


df_letras["nlp_obj"] = df_letras.apply(lambda x: NlpLetra(x['letra']),
                                        axis=1)
df_letras["total_palavras"] = df_letras.apply(lambda x:
    len(x['nlp_obj'].texts()), axis=1)
df_letras["palavras_unicas"] = df_letras.apply(lambda x:
    len(set(x['nlp_obj'].texts())), axis=1)

    
lista_albums = list(df['Álbum'].unique())


# Este df_nlp parece uma boa forma de analizar
# teste com 1 por amor 2 por dinheiro já mostra algumas inconsistências no
# reconhecimento. Ex deus como conjunção subordinativa ("pos SCONJ")
# irmãos e olhos em pos SYM
# alguns DET em ADJ em diário de um detento
# A solução é basicamente treinar outro modelo?


nlp_t = df_letras.iloc[15, 4]
df_nlp = pd.DataFrame({"pos":nlp_t.pospeech(),
                       "tag":nlp_t.tags(),
                       "text": nlp_t.texts()})

print(df_nlp['pos'].value_counts())








# após correção, apenas os albums importantes ficaram aparecendo
# verificados, Escolha seu caminho que tem 2 letras
# no EP repete 3x a musica voz ativa 

#df_albums = df_letras.groupby('Álbum')
#
#  Album                               num_letras
# Nada como um Dia após o Outro Dia    20
# Cores & Valores                      14
# Sobrevivendo no Inferno              11
# Holocausto Urbano                     6
# Raio X Brasil                         6
# Escolha o seu Caminho                 2
# singles                               2
