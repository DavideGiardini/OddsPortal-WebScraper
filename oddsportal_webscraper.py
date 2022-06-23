from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import unicodedata
import re

op = webdriver.ChromeOptions()
driver = webdriver.Chrome()
# First we have to open the website in order to change the time zone
driver.get("http://www.oddsportal.com/set-timezone/11/")
sleep(10)

def scrape_links(addr_s):
    links_s = []
    names_s = []
    score_s = []
    cat = {}
    driver.get(addr_s)
    sleep(1)
    soup_s = BeautifulSoup(driver.page_source, features="html.parser")

    # building dictionary category-date
    for a in soup_s.findAll("span", class_="datet"):
        next_sibling = str(a.next_sibling)[3:]
        if next_sibling == "e":
            category = "Regular Season"
        elif next_sibling == "Promotion - Play Offs":
            category = "Play-In"
        else:
            category = next_sibling
        # se in una data sono state fatte partite di più categorie occorre risolvere manualmente
        if a.text in cat:
            cat[a.text] = "please control"
            continue
        if a.text[0].isnumeric():
           cat[a.text] = category
        else:
            b = a.text.split(", ")[1] + "2022"
            cat[b] = category

    for a in soup_s.findAll("td", class_="name table-participant"):
        if a.text[0] == " ":
            continue
        # Usiamo normalize() per togliere "\xa0" dalla fine di ogni stringa all'interno di names
        names_s.append(unicodedata.normalize("NFKD", a.text).rstrip())
        for b in a('a'):
            link = "https://www.oddsportal.com" + b.get('href', None)
            links_s.append(link)
    for a in soup_s.findAll("td", class_="center bold table-odds table-score"):
        score_s.append(a.text)

    return names_s, links_s, cat


def scrape_odds(link_s):
    # AH
    # Costruisce il link per ah e apre la pagina
    link_ah = link_s + "#ah;1"
    driver.get(link_ah)
    content = driver.page_source
    soup_s = BeautifulSoup(content, features="html.parser")
    # trova le informazioni
    ratings_s = []
    for a in soup_s.findAll("div", class_="table-container"):
        b = a.text.find("(")
        if b == -1 or a.text[b+1] == "0":
            continue
        h = 1
        for c in a('a'):
            if h % 4 == 0:
                continue
            ratings_s.append(c.text)
            h += 1
    # in caso di errore: print error
#    if not ratings_s:
#            print("can't find Asian Handicap at: " + link_s)
    j = 0
    diff_ah = 1000
    best = 1000
    # trova i numeri più vicini
    while j < len(ratings_s):
        diff_n = abs(float(ratings_s[j + 1]) - float(ratings_s[j + 2]))
        if diff_n < diff_ah:
            diff_ah = diff_n
            best = j
        j += 3
    # controllo che la differenza sia minore di 0.20
    if diff_ah >= 0.20:
        ah = "NULL"
    else:
        ah = ratings_s[best].split(" ")[2]
    if diff_ah == 1000:
        diff_ah = "Not Found"
    else:
        diff_ah = round(diff_ah, 2)

    # SCORE_Q
    score_q = ""
    is_ot = ""
    score_ot = ""
    score_f = ""
    # trova il paragrafo chiamato "result"
    for a in soup_s.findAll("p", class_="result"):
        # al suo interno trova la posizione della parentesi
        txt = a.text
        p = txt.find("(")
        txt_s = txt.split(" ")
        if txt[p - 2] == "T":
            score_f = txt_s[2]
            is_ot = "TRUE"
            score_ot = txt_s[4]
            u = txt.find(") (")
            score_q = txt[u + 2:]
        else:
            score_f = txt_s[2]
            score_q = txt[p:]
            is_ot = "FALSE"
            score_ot = ""

    # DATE
    date = ""
    for a in soup_s.findAll("p", class_="date"):
        # al suo interno prendiamo la data dividendo la stringa in 3 parti ai livelli delle virgole e prendendo quella centrale
        date = a.text.split(', ')[1]
        # In questo modo togliamo i doppi spazi dalle date
        date = re.sub(' +', ' ', date).strip()

    # O/U
    # Costruzione del link per over-under e apertura pagina
    link_ou = link_s + "#over-under;1"
    driver.get(link_ou)
    # We have to refresh the page, otherwise the driver remains in the Asian Handicap page (for some reason)
    driver.refresh()
    content = driver.page_source
    soup_ou = BeautifulSoup(content, features="html.parser")
    ratings_ou = []
    for a in soup_ou.findAll("div", class_="table-container"):
        b = a.text.find("(")
        if b == -1 or a.text[b + 1] == "0":
            continue
        h = 1
        for c in a('a'):
            if h % 4 == 0:
                continue
            ratings_ou.append(c.text)
            h += 1
    # in caso di errore: print error
#    if not ratings_ou:
#            print("can't find Over/Under at: " + link_s)
    j = 0
    diff_ou = 1000
    best = 1000
    # trova i numeri più vicini
    while j < len(ratings_ou):
        diff_n = abs(float(ratings_ou[j + 1]) - float(ratings_ou[j + 2]))
        if diff_n < diff_ou:
            diff_ou = diff_n
            best = j
        j += 3
    # controllo che la differenza sia minore di 0.20
    if diff_ou >= 0.20:
        ou = "NULL"
    else:
        ou = ratings_ou[best].split(" ")[1]
    # se la differenza è ancora uguale a 1000 ritorna il valore "not found"
    if diff_ou == 1000:
        diff_ou = "Not Found"
    else:
        diff_ou = round(diff_ou, 2)

    return ah, diff_ah, score_q, date, ou, diff_ou, is_ot, score_ot, score_f


def correction(df):
    # Tentativo di correzione dei link mancanti
    print("correggo i dati mancanti")
    null_ou = pd.isnull(df["OU"])
    null_ah = pd.isnull(df["AH"])
    nulls_ou = df[null_ou].index.tolist()
    nulls_ah = df[null_ah].index.tolist()
    if nulls_ou:
        for i in nulls_ou:
            link_corr = df.loc[i, "link"]
            corr = scrape_odds(link_corr)
            df.loc[i, "OU"] = corr[4]
            df.loc[i, "diff OU"] = corr[5]
    if nulls_ah:
        for i in nulls_ah:
            link_corr = df.loc(i, "link")
            corr = scrape_odds(link_corr)
            df.loc[i, "AH"] = corr[0]
            df.loc[i, "diff AH"] = corr[1]
    return df


# Loop through seasons and pages to retrieve all the links, the matches, the scores and build the dictionary Date-PlayOffs
h = 3
# loop through seasons
while h < 12:
    names = []
    links = []
    score = []
    cat = {}
#    if h == 0:
#        addr_s = "https://www.oddsportal.com/basketball/usa/nba/results/"
#    else:
    addr_s = "https://www.oddsportal.com/basketball/usa/nba-" + str(2021-h) + "-" + str(2022-h) + "/results/"
    # loop through pages
    i = 0
    while True:
        if i > 0:
            addr = addr_s + "#/page/" + str(i + 1) + "/"
        else:
            addr = addr_s
        tup = scrape_links(addr)
        # break if last page is reached
        if not tup[0]:
            break
        names.extend(tup[0])
        links.extend(tup[1])
        cat.update(tup[2])
        i += 1
    # Opens all the links we just retrieved and downloads all the infos
    AH = []
    diff_ah = []
    score_q = []
    date = []
    OU = []
    diff_ou = []
    is_ot = []
    score_ot = []
    score = []
    for link in links:
        print(f"Scraping odds: {links.index(link) + 1} / {len(links)}")
        tup = scrape_odds(link)
        AH.append(tup[0])
        diff_ah.append(tup[1])
        score_q.append(tup[2])
        date.append(tup[3])
        OU.append(tup[4])
        diff_ou.append(tup[5])
        is_ot.append(tup[6])
        score_ot.append(tup[7])
        score.append(tup[8])
    print("writing the DataFrame for" + str(2021-h) + "-" + str(2022-h))
    category = []
    for i in date:
        if i == '':
            category.append('')
        else:
            category.append(cat[i])
    df = pd.DataFrame({'Names': names,
                       'link': links,
                       'Score': score,
                       'Score q': score_q,
                       'OverTime': is_ot,
                       'Score OT': score_ot,
                       'date': date,
                       'category': category,
                       'AH': AH,
                       'diff AH': diff_ah,
                       'OU': OU,
                       'diff OU': diff_ou, })
    # Se la stagione è la 2014-2015 non vogliamo la correzione, perché nel sito non sono mai presenti ah/ou
    if not h == 7:
        df = correction(df)
    save_addr = "C:/Users/david/Desktop/NBA odds/" + str(2021-h) + "-" + str(2022-h) + ".csv"
    df.to_csv(save_addr, index=False, encoding='utf-8')

    h += 1


driver.close()
