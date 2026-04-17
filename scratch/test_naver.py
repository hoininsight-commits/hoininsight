import requests
from bs4 import BeautifulSoup

def test_naver_quant():
    url = "https://finance.naver.com/sise/sise_quant.naver?sosok=0"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'lxml')
    
    table = soup.find('table', class_='type_2')
    rows = table.find_all('tr')
    
    # 헤더 확인
    header_row = rows[0]
    headers = [th.text.strip() for th in header_row.find_all('th')]
    print(f"Headers: {headers}")

    for row in rows[1:10]: # 상위 10개만
        cols = row.find_all('td')
        if len(cols) < 5: continue
        
        name = cols[1].text.strip()
        # 거래대금 컬럼 찾기
        for i, col in enumerate(cols):
            val = col.text.strip()
            print(f"Col[{i}]: {val}", end=" | ")
        print("\n" + "-"*50)

if __name__ == "__main__":
    test_naver_quant()
