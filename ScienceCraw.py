#!usr/bin/env python
#coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.proxy import *
import re

class CWebRender(webdriver.Firefox):
    def __init__(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.proxy.type', 1)
        profile.set_preference('network.proxy.http', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        #profile.set_preference('network.proxy.http_port', 8080)
        profile.set_preference('network.proxy.ssl', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        #profile.set_preference('network.proxy.ssl_port', 8080)
        profile.update_preferences()
        webdriver.Firefox.__init__(self, profile)

    def closeUrl(self):
        self.close()
        self.quit()

class CSciencePage():
    def __init__(self):
        self.pattern = re.compile('&uid=(\d+)')
        self.pagePattern = re.compile('-(\d+).html')
        self.url = ''

    def getPage(self, url, mCWebRender):
        self.url = url
        mCWebRender.get(url)

    def getTitle(self, mCWebRender):
        title = mCWebRender.find_element_by_xpath("//h1[@class='ph']")
        if title:
            return title.text
        return ''

    def getContent(self, mCWebRender):
        content = mCWebRender.find_element_by_xpath("//div[@id='blog_article']")
        if content:
            return content.text
        return ''

    def getRecPersons(self, mCWebRender):
        '''
        Get the recommenders for this article.
        '''
        recModule = mCWebRender.find_element_by_xpath("//h4[@class='bbs pbn']")
        persons = recModule.find_elements_by_xpath("span/a")
        persons_id = []
        for person in persons:
            href = person.get_attribute("href")
            uidlist = self.pattern.findall(href)
            if len(uidlist):
                persons_id.append(int(uidlist[0]))
        return persons_id

    def nextPage(self, mCWebRender):
        '''
        Get the next page comment.
        '''
        commentModule = mCWebRender.find_element_by_id("discusscontent")
        persons = self.getCommentPersons(commentModule)
        page = 1
        blogId = self.pagePattern.findall(self.url)
        blogId = int(blogId[0])
        while True:
            page += 1
            nextpage = commentModule.find_elements_by_link_text(u'下一页')
            #nextpage = commentModule.find_element_by_xpath("//discusscontent/*/p/a[@onclick='viewpage(%d, %d)']" % (page, blogId))
            if len(nextpage) == 0:
                break
            print nextpage[0].text
            nextpage[0].click()
            #commentModule = mCWebRender.find_element_by_id("discusscontent")
            persons.extend(self.getCommentPersons(commentModule))
        return persons

    def getCommentPersons(self, commentModule):
        '''
        Get the commenter for this article.
        '''
        commentPersons = commentModule.find_elements_by_xpath("dl/dt")
        persons = []
        for person in commentPersons:
            idModule = person.find_element_by_xpath("a")
            href = idModule.get_attribute("href")
            uidlist = self.pattern.findall(href)
            timeModule = person.find_element_by_xpath("span[@class='xg1 xw0']")
            if len(uidlist):
                person_id = int(uidlist[0])
                person_time = timeModule.text
                persons.append([person_id,person_time])
        return persons

def main():
    url = "http://blog.sciencenet.cn/blog-99934-855869.html"
    url = "http://blog.sciencenet.cn/blog-660333-632151.html"
    mCWebRender = CWebRender()
    mCSciencePage = CSciencePage()
    mCSciencePage.getPage(url, mCWebRender)
    title = mCSciencePage.getTitle(mCWebRender)
    print '*'*50
    print title
    article = mCSciencePage.getContent(mCWebRender)
    print '*'*50
    print article
    recPersons = mCSciencePage.getRecPersons(mCWebRender)
    print '*'*50
    print recPersons

    print '*'*50
    persons = mCSciencePage.nextPage(mCWebRender)
    print 'Persons Number:', len(persons)
    mCWebRender.closeUrl()
    
if __name__ == '__main__':
    main()


