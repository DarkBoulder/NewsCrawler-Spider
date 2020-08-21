import requests
from bs4 import BeautifulSoup
import re
import xlwt


class News:
    def __init__(self, searchName, searchArea='news'):
        self.head = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52',
            'Cookie': "SGUID=1567991865627_35687923; sso_info=v02m6alo5qztKWRk5yljpOQpZCToKWRk5iljoOgpZCjnLKNs4y2jKOYso2DmLCJp5WpmYO0so2zjLaMo5iyjYOYsA==; SINAGLOBAL=114.247.56.147_1561166799.522454; __gads=ID=c8bbe13e7ffe5dea:T=1582037208:S=ALNI_MYdLPR0-weziylssNrmcrBoNM9JBQ; FSINAGLOBAL=114.247.56.147_1561166799.522454; vjuids=-71d7a0f2.16dd7c6f873.0.55790055dfe03; U_TRS1=00000093.cc1552df.5d10d2ac.8d8eb40f; UM_distinctid=1704387665e4af-034de02b15257f-784a5935-109e81-1704387665fe7b; lxlrttp=1578733570; gr_user_id=1720c92e-9bf3-4cbe-b623-e0e6ff13b998; grwng_uid=76c0ca9d-fe24-4377-abd5-133d753244e7; SCF=AqqyiDNuuZCW3pm-CR_fS8Wf31vuUOmoxtTjSoUioY0h2Z8kwDGP7HytSl4imkgB4IcxdSLdqqJ_fqiZBqs1Pwg.; _ga=GA1.3.91822075.1590054596; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5i0sSw7IXPXovqReQ7dqgF; SUB=_2AkMpHoj0f8NxqwJRmP4Tz2rlaYVxzw_EieKfQnkvJRMyHRl-yD9jqhU5tRB6Ap6mG5n54ekEsYELBHGUaKY0wCoLShjR; UOR=,,; vjlast=1596593309; Apache=106.3.196.29_1597228826.415000; ULV=1597228827048:31:1:1:106.3.196.29_1597228826.415000:1591001869288; beegosessionID=9d7b37ab193b88f7da29da1e24281565; WEB5_OTHER=3bcc72c6e7b514813bc37f8c88915c78; _gid=GA1.3.219288575.1597232926; rotatecount=1"
        }
        self.searchName = searchName
        self.searchArea = searchArea
        self.UrlData = []  # 爬取新闻url的存储
        self.TitleData = []  # 爬取新闻标题的存储
        self.NewsData = []  # 爬取新闻数据的存储
        self.pageCount = 0

    def get_page_count(self):
        url = 'https://search.sina.com.cn/?'  # 查找的关键字url
        params = {
            'q': self.searchName,
            'range': 'all',
            'c': 'news',
            'sort': 'time',
        }
        response = requests.get(url=url, params=params)
        # response.encoding = 'utf-8'
        html = response.text
        # 得到的网页，判断是否有找到news
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup)
        # 爬取是否有l_v2这个class，如果有代表有数据，否则无
        try:
            page = soup.select('.l_v2')[0].text
        except Exception as e:
            page = ''
            print(e)
        if page != '':
            purl = ''
            pageCount = re.findall(r'[0-9]\d*', page)
            # print(pageCount)
            for x in pageCount:
                purl = purl + x
            # print(purl)
            self.pageCount = int(purl) // 10 + 1  # 总的页数 = 总条目数 // 每页条目数 + 1
        else:
            self.pageCount = 0
        return self.pageCount

    # get 整页的news
    def get_news_data(self):
        url = 'https://search.sina.com.cn/?q={}&c={}&ie=utf-8&sort=time&page={}'
        count = input('共找到{}页信息，请输入需要爬取的页数，不输入按q继续【爬取全部】：'.format(self.pageCount))
        if count == 'q':
            count = self.pageCount
        print('开始爬取......')

        for x in range(1, int(count) + 1):
            responses = requests.get(url.format(self.searchName, self.searchArea, x), headers=self.head)
            # print(responses)
            # print(url.format(self.searchName,self.searchArea,x))
            html = responses.text
            soup = BeautifulSoup(html, 'html.parser')
            reg = soup.select('h2 > a')  # 搜索h2标签下的a标签，得到列表，每个元素是字符串
            newsUrl = re.findall('<a href="(.*?)" target="_blank">.*?</a>', str(reg), re.S)  # 新闻url
            newsTitle = re.findall('<a href=".*?" target="_blank">(.*?)</a>', str(reg), re.S)  # 新闻标题，font color 未处理
            """newsTitle = re.sub('<.*?>', '', str(newsTitle))
            # print(newsTitle)
            newsTitle = newsTitle[1:len(newsTitle) - 1].replace("'", '')
            # print(newsTitle)
            titleData = newsTitle.split(',')  # 新闻标题"""
            titleData = []
            for ele in newsTitle:
                titleData.append(re.sub('<.*?>', '', str(ele)))
            # print(len(titleData))
            for i in range(len(titleData)):
                self.TitleData.append(titleData[i])
            for i in range(len(newsUrl)):
                self.UrlData.append(newsUrl[i])

    def get_news_content(self, url):
        """
        根据得到的url，获取二级新闻页面的内容
        :param url:
        :return:
        """
        responses = requests.get(url, headers=self.head)
        responses.encoding = 'utf-8'
        html = responses.text
        soup = BeautifulSoup(html, 'html.parser')
        reg = soup.select('.article > p')
        if len(reg) == 0:
            reg = soup.select('#artibody > p')
        newsData = []  # 用来装一条newscontent,二维
        newsData1 = []  # 用来装一条newscontent,1维
        for x in reg:
            if len(x) > 0:
                data = re.findall(r'<p cms-style="font-L">(.*?)</p>', str(x), re.S)
                if len(data) == 0:
                    data = re.findall(r'<p><font>(.*?)</font></p>', str(x), re.S)
                if len(data) == 0:
                    data = re.findall(r'<p>　　<font>(.*?)</font></p>', str(x), re.S)
                """if len(data) == 0:
                    print(x)"""
                if len(data) > 0:
                    mydata = re.sub('<.*?>', '', str(data[0]))
                    newsData.append(mydata)

        # 将二维数组转成一维存储入NewsData(新闻content)
        if len(newsData) == 0:
            newsData1 = []
        else:
            # print('newsData1 = {}'.format(newsData) )
            for i in range(len(newsData)):
                if newsData[i] != '':
                    newsData1.append(newsData[i] + '\n')
                else:
                    continue
        self.NewsData.append(newsData1)

    # 封装后的入数据方法
    def final_func(self):
        for i in range(len(self.UrlData)):
            self.get_news_content(self.UrlData[i])
            if (i + 1) % 10 == 0:
                print("第{}页完成".format((i+1)//10))
        self.save_data_excel()

    # 将finalData存储到excel里面
    def save_data_excel(self):
        urldata = self.UrlData
        newsdata = self.NewsData
        titledata = self.TitleData
        ExcelTitle = ['编号', '新闻标题', 'URL', '新闻内容']
        row = 0
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet('包含\"' + self.searchName + '\"的新闻', cell_overwrite_ok='True')
        # 先写入第一行
        print('开始写入数据到excel....')
        for i in range(len(ExcelTitle)):
            sheet.write(row, i, ExcelTitle[i])

        cnt = 0
        for j in range(len(self.TitleData)):
            if len(newsdata[j]) == 0:
                cnt += 1
            else:
                row += 1
                sheet.write(row, 0, row)
                sheet.write(row, 1, titledata[j])
                sheet.write(row, 2, urldata[j])
                sheet.write(row, 3, newsdata[j])
        book.save('数据.xls')
        print('写入数据完毕！其中有{}行为空'.format(cnt))


if __name__ == '__main__':
    name = input('请输入要爬取的关键词:')
    news = News(name)
    news.get_page_count()  # 得到总页数
    news.get_news_data()
    news.final_func()
