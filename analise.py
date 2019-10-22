#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 16:24:24 2019

@author: root
"""
import os
import pandas as pd
import spacy

nlp = spacy.load("pt_core_news_sm")

pd.options.display.max_rows = 100
pd.options.display.max_columns = 50
caminho_arquivo = "scrapping" + os.sep + "data.json"
df = pd.read_json(caminho_arquivo)

df_letras = df.loc[~df['letra'].isnull()].copy()


class NlpLetra:
    """
        Objeto que busca no modulo spaCy a interpretaçao da letra.
    """

    def __init__(self, letra):
        self.__nlp = nlp(letra)
        self.__excluir = ["SPACE", "PUNCT"]

    def texts(self):
        return [token.text for token in self.__nlp \
                if token.pos_ not in self.__excluir]

    def pospeech(self):
        return [token.pos_ for token in self.__nlp\
                if token.pos_ not in self.__excluir]

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

#t = df.iloc[0]['letra']
#test = nlp(t)
#texts = [token.text for token in test]
#pos = [token.pos_ for token in test]
#deps = [token.dep_ for token in test]
## CAMINHO IMPORTANTE, Reconhecimento de entidades mencionadas (REM)
## https://teses.usp.br/teses/disponiveis/45/45134/tde-23052013-104248/publico/dissertacao_rem_wesley_seidel.pdf
#ents = [(entity, entity.label_) for entity in test.ents]
    