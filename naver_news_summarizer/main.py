from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from text_rank import TextRank

# 불필요한 텍스트를 잘라낼 때 사용할 수 있는 token의 list 및 정규식입니다.
delReg = "[\\\\{}<>/!@#$%^&*='_■]"
naverDelList = ['서울연합뉴스', '사진연합뉴스', '이데일리', '플레이어', '뉴스1코리아', '서울경제', '오류를 우회하기 위한 함수 추가', '본문 내용', '무단 전재 및 재배포 금지', '사진', 'ⓒ', '세계를 보는 창', '경제를 보는 눈', '아시아경제', '무단전재',
                '배포금지.', '뉴스가 재밌다', '세상의 모든 재미', '티잼', '네이버 뉴스', '뉴스 스탠드에서도 만나세요', '뉴시스 페이스북 트위터', '공감언론', '뉴시스통신사', '( 연합뉴스)',
                '02)3701-5555', '구독신청:', '대한민국 오후를 여는 유일석간', '문화일보', '모바일 웹', '문화닷컴 바로가기', '▶', '()',  '【', '】', '.."', '[', ']', '©', '  ']

'''
사이트의 정치 뉴스 부분을 크롤링 해주는 클래스입니다.
'''
class Crawler:
    def __init__(self, _site):
        self.site = _site

    def Crawling(self):
        self.url = ''
        self.divClass = ''

        if self.site == 'naver' or self.site == 'Naver':

            self.url = 'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=100'
            self.divClass = 'section_headline headline_subordi'
            response = urlopen(self.url)
            plain_text = response.read()
            soup = BeautifulSoup(plain_text, 'html.parser')

            politic_news = soup.find_all('div', class_=self.divClass)

            return politic_news


'''
입력한 텍스트를 요약해주는 클래스입니다.
'''
class Summarizer:
    def __init__(self, _news):
        self.news = _news

    def summarize(self):
        for div_link in self.news:
            tmp_link_list = div_link.find_all('a')
            # news_list = []
            print('\n\n---- 분기 ----')

            for news_link in tmp_link_list[1:]:
                if len(news_link.text) <= 10:
                    continue
                contentsList = self.getTextListFromURL(news_link.get('href'))
                for i in range(0, len(contentsList)):
                    contentsList[i] = self.trimContents('naver', contentsList[i])

                print(news_link.text, ' >> ')
                print(self.summarizeTextList(contentsList, 5), '\n')


    '''
    뉴스 내용을 가져와 불필요한 내용을 잘라냅니다.
    불필요한 내용을 자를 때 사용되는 token list는 site마다 다르며, 
    listName을 통해 어떤 사이트의 뉴스를 가져오는지 알 수 있습니다
    '''
    def trimContents(self, listName, contents):
        global naverDelList

        contents = re.sub(delReg, ' ', contents)

        if listName == 'naver':
            curList = naverDelList
        else:
            curList = naverDelList

        for tok in curList:
            # print(tok)
            contents = contents.replace(tok, '')
        return contents

    '''
    TextRank 알고리즘을 통해 글을 요약합니다.
    전체 글을 절반으로 나누고, 각 부분에서 중요도가 높은 문장으로 20문장 씩 뽑아낸 뒤,
    총 40 문장에서 중요한 문장을 또 뽑아냅니다.
    몇 문장을 뽑아낼지는 lines 파라미터로 정할 수 있습니다.
    '''
    def summarizeText(self, text, lines):
        length = len(text)
        text_div1 = text[0:int(length / 2)]
        text_div2 = text[int(length / 2):int(length - 1)]

        textrank_div1 = TextRank(text_div1)
        textrank_div2 = TextRank(text_div2)
        textresult_div1 = textrank_div1.summarize(10)
        textresult_div2 = textrank_div2.summarize(10)
        textresult = textresult_div1 + textresult_div2
        resultrank = TextRank(textresult)

        return resultrank.summarize(lines)

    def summarizeTextList(self, textList, lines):
        length = len(textList)
        textList1 = textList[0:int(length / 2)]
        textList2 = textList[int(length / 2):int(length - 1)]

        text1 = ''
        text2 = ''
        for sentence in textList1:
            text1 += sentence+' '
        for sentence in textList2:
            text2 += sentence+' '

        textrank1 = TextRank(text1)
        textrank2 = TextRank(text2)
        textresult1 = textrank1.summarize(10)
        textresult2 = textrank2.summarize(10)
        textresult = textresult1 + textresult2
        resultrank = TextRank(textresult)

        return resultrank.summarize(lines)

    '''
    뉴스 기사 하나의 주소로부터 기사 내용을 parsing 하고, list를 반환합니다.
    BeautifulSoup를 이용합니다.
    '''
    def getTextListFromURL(self, URL):
        source_code_from_URL = urlopen(URL)
        text_from_source_code = source_code_from_URL.read()
        soup = BeautifulSoup(text_from_source_code, 'html.parser', from_encoding='utf-8')
        resultList = []

        for item in soup.find_all('div', id='articleBodyContents'):
            strList = item.find_all(text=True)
            for i in range(0,len(strList)):
                specialIdx = str(strList[i]).find('▶')
                endIdx = str(strList[i]).find('다.')
                if endIdx is not -1 and specialIdx is -1:
                    strList[i] = strList[i][0:endIdx+2]
                else:
                    strList[i] = ''

            for sentence in strList:
                if sentence is not '':
                    resultList.append(sentence)

        return resultList

'''
Crawer()를 통해 뉴스 기사의 요약본을 가져올 수 있습니다.
파리미터로 naver, daum등이 들어갈 수 있습니다.
'''
if __name__ == '__main__':
    naverCrawler = Crawler('naver')
    naverNews = naverCrawler.Crawling()

    Summarizer(_news=naverNews).summarize()
