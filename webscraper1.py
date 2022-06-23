from selenium import webdriver
from bs4 import BeautifulSoup


def scrape():
    ratings_s = []
    odds_s = []
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options=op)
    driver.get("https://www.oddsportal.com/basketball/usa/nba/new-york-knicks-philadelphia-76ers-25AGjGuP/#ah;1")
    content = driver.page_source
    soup_s = BeautifulSoup(content, features="html.parser")
    for a in soup_s.findAll("span", class_="avg chunk-odd nowrp"):
        if a.text != "":
            ratings_s.append(a.text)
    if not ratings_s:
        scrape()
    for a in soup_s.findAll("a", class_=False, id=False, text=True):
        odds_s.append(a.text)
    i = 0
    diff = 1000
    while i < len(ratings_s) / 2:
        diff_n = abs(float(ratings_s[2 * i + 1]) - float(ratings_s[2 * i]))
        if diff_n < diff:
            diff = diff_n
            best = i
        i += 1
    n = odds_s.index(ratings_s[2 * best])
    return odds_s[n - 1][15:19]


AH = scrape()
print(AH)







# df = pd.DataFrame({'Product Name':products,'Price':prices,'Rating':ratings})
# df.to_csv('products.csv', index=False, encoding='utf-8')
