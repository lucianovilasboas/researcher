# Importando as bibliotecas
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
from matplotlib import pyplot as plt
import numpy as np
import os

path_to_save = "./"

# definição das funções
def dblp2dataframe(q,h=1000):
    """
        Busca na api de publicações da DBLP a lista de artigos a partir de palavras chave.
        q = key word
    """
    pp = requests.get('https://dblp.org/search/publ/api?q={}&h={}'.format(q,h))
    soup = BeautifulSoup(pp.text, 'html.parser')
    article_list = soup.find_all('hit')
    data=[]
    for t in article_list:
        dblp_id   = t.get('id')
        authors   = [author.text for author in t.find_all('author')] if t.find('authors') else [];
        year      = t.find('year').text if t.find('year') else "";    
        title     = t.find('title').text if t.find('title') else "";
        venue     = t.find('venue').text if t.find('venue') else "";        
        pages     = t.find('pages').text if t.find('pages') else "";
        type_     = t.find('type').text if t.find('type') else "";
        key       = t.find('key').text if t.find('key') else "";
        url       = t.find('url').text if t.find('url') else "";    
        doi       = t.find('doi').text if t.find('doi') else ""; 
        ee        = t.find('ee').text if t.find('ee') else ""; 
        
        data.append([year,dblp_id,title,authors,venue,pages,type_,key,url,doi,ee]);

    return pd.DataFrame(data, columns=['year','dblp_id','title','authors','venue','pages','type_','key','url','doi','ee']).sort_values(by='year', ascending=False)


def dblp2dataframe_byauthor(q,h=100):
    """
        Busca na api de publicações da DBLP a lista de artigos a partir de um nome de author.
        q = author name
    """
    pp = requests.get('https://dblp.org/search/author/api?q={}&h={}'.format(q,h))
    soup = BeautifulSoup(pp.text, 'html.parser')
    article_list = soup.find_all('info')
    data=[]
    for t in article_list:
        author  = t.find('author').text if t.find('author') else "";
        alias   = t.find('alias').text if t.find('alias') else "";  
        url     = t.find('url').text if t.find('url') else "";    
        data.append([author, alias, url]);

    return pd.DataFrame(data, columns=['author','alias','url']).sort_values(by='author', ascending=False)


def df2csv(name, df):
    """
        Salva um pandas dataframe como arquivo csv
        name = filename
    """
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)
    df.to_csv("{}{}".format(path_to_save,name),index=False);
    
    
def get_papers_and_csv_save(keyword_list = []):
    """
        Busca na api de publicações da DBLP a lista de artigos a partir de palavras chave.
        key_word_list = list of keyword
    """
    sum_ = 0
    for key_word in key_words:
        df_ = dblp2dataframe(keyword)
        df2csv("{}.csv".format(keyword.replace(" ","_")), df_)
        print("\t",key_word,"=> ",df_.shape[0],"saved...")
        sum_+=df_.shape[0]
    print("Total: ",sum_)
    
    
def merge_dfs(key_word_list = []):
    """
     lendo todos os arquivos e juntando em um único dataframe
    """
    dff_ = pd.read_csv("{}{}.csv".format(path_to_save,key_words[0].replace(" ","_")))
    dff_['key_word'] = [ key_words[0] ] * dff_.shape[0]

    for i in range(1,len(key_words)):
        dfx_ = pd.read_csv( "{}{}.csv".format(path_to_save,key_words[i].replace(" ","_")) )
        dfx_['key_word'] = [ key_words[i] ] * dfx_.shape[0]
        dff_ = pd.concat([dfx_, dff_])
    # ordena pelo ano de publicação    
    dff_.sort_values("year", inplace = True, ascending=False) 
    return dff_

def group_by_venue_and_return_list(df, n):
    dff_group_venue = dff_.groupby(['venue']).count().sort_values(by='year', ascending=False)
    venue_list = [i for i in dff_group_venue[dff_group_venue['year']>=n].index]
    return venue_list

def filter_by_venues(venue_list, df):
    return df[df['venue'].isin(venue_list)]

def get_top_authors(df,top=100):
    """
        Retorna a lista dos top autores mais frequentes a partir de um dataframe.
        df = pandas dataframe
    """
    autores = []
    for authors in df['authors']:
        # autores += str(authors).replace("['","").replace("']","").split("', '")
        autores += authors
        
    frequency = Counter(autores)
    authors_top_ = [f[0] for f in frequency.most_common(top)]

    return authors_top_

def get_top_authors_freq(df,top=100):
    """
        Retorna a lista de tuplas (autor + freq) dos top autores mais frequentes a partir de um dataframe
        df = pandas dataframe
    """
    autores = []
    for authors in df['authors']:
        # autores += str(authors).replace("['","").replace("']","").split("', '")
        autores += authors
        
    frequency = Counter(autores)

    return frequency.most_common(top)

def filter_by_top_authors(df, top=100):
    """
        filtering by top authors
        df = pandas dataframe
    """ 
    authors_top_frequency = get_top_authors(df,top)
    titles = set()
    for author in authors_top_frequency:
        tt = df[ df['authors'].str.contains(author)]['title']
        for t in tt:
            titles.add(t)

    return df[df['title'].isin(list(titles))]


def get_bibtex_refs(df):
    """
        get bibtex refs
        df = pandas dataframe
    """ 
    bib = []
    for url in df['url']:
        url_   = url.split("/rec/")
        url_   = "{0}/rec/bibtex/{1}".format(url_[0],url_[1])
    #   print(url_)
        page   = requests.get(url_)
        soup   = BeautifulSoup(page.text, "html.parser")
        bibtex = soup.find(class_="verbatim select-on-click")
    #   print(bibtex.text, "\n")
        bib.append(bibtex.text)
    return bib

def get_and_save_bibtex_refs(df):
    """
        get and save bibtex refs
        df = pandas dataframe
    """
    with open('{}dblp.bib'.format(path_to_save), 'w') as file:
        for url in df['url']:
            url_   = url.split("/rec/")
            url_   = "{0}/rec/bibtex/{1}".format(url_[0],url_[1])
        #   print(url_)
            page   = requests.get(url_)
            soup   = BeautifulSoup(page.text, "html.parser")
            bibtex = soup.find(class_="verbatim select-on-click")      
        #   print(bibtex.text, "\n")
            file.write(bibtex.text)
            file.write("\n")

def plot_top_authors(df,top=20):
    """
        Plot top authors from dataframe 
        df = pandas dataframe
    """
    top_frequency = get_top_authors_freq(df,top)
    index = [f[0] for f in top_frequency]
    freq  = [f[1] for f in top_frequency]
    df2 = pd.DataFrame({"# Publications":freq}, index=index)
    ax = df2.plot.barh(rot=0)

def get_first_authors(df):
    """
        Lista os primeiros autores em um dataframe de artigos
    """
    pass
    