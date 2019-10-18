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
df_analise = df.loc[~df['letra'].isnull()].copy()

def analise_lemma(doc):
    lemmas = [token.lemma_ for token in doc]
    poss = [token.pos_ for token in doc]
    deps = [token.dep_ for token in doc]
    df = pd.DataFrame({"lemma":lemmas,
                       "tag": poss,
                       "dep": deps
                       }
    )
    
    return df.groupby("lemma").agg({"tag": lambda x: list(x),
                                    "dep": lambda x: list(x)
                                    }).reset_index()
    
for i in range(len(df_analise)):
    print("""
          {}.
          
          {}
          ---------""".format(df_analise.iloc[i]['Canção'], 
          df_analise.iloc[i]['letra']))
    
t = df_analise.iloc[0]['letra']
test = nlp(t)
texts = [token.text for token in test]
pos = [token.pos_ for token in test]

# coisas que tirei do site do spacy 
#for token in test:
#    # Get the token text, part-of-speech tag and dependency label
#    token_text = token.text
#    token_pos = token.pos_
#    token_dep = token.dep_
#    # This is for formatting only
#    print("{:<12}{:<10}{:<10}".format(token_text, token_pos, token_dep))
#
#for ent in test.ents:
#    # Print the entity text and label
#    print(ent.text, ent.label_)