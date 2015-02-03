#!usr/bin/env python
#coding:utf-8

import re
import time
from WebRender import CWebRender
from multiprocessing import Pool
from Database import CDatabase
from CommonFunc import connectDb
import string

delset = string.punctuation
transtab = string.maketrans(delset, ','*len(delset))

class CSciencePage():
    def __init__(self):
        self.pattern = re.compile('&uid=(\d+)')
        self.pagePattern = re.compile('-(\d+).html')
        self.url = ''

    def getPage(self, url, mCWebRender):
        self.url = url
        mCWebRender.get(url)

    def getTitle(self, mCWebRender):
        title = mCWebRender.find_elements_by_xpath("//h1[@class='ph']")
        if len(title):
            return title[0].text
        return ''

    def getContent(self, mCWebRender):
        content = mCWebRender.find_elements_by_xpath("//div[@id='blog_article']")
        if len(content):
            return content[0].text
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

    def getAllComments(self, mCWebRender):
        '''
        Get all the pages comments.
        '''
        commentModule = mCWebRender.find_element_by_id("discusscontent")
        persons = self.getCommentPersons(commentModule)
        while True:
            if not self.nextPage(mCWebRender):
                break
            persons.extend(self.getCommentPersons(commentModule))
        return persons

    def nextPage(self, commentModule):
        '''
        Get the next page comment.
        '''
        nextpage = commentModule.find_elements_by_link_text(u'下一页')
        #nextpage = commentModule.find_element_by_xpath("//discusscontent/*/p/a[@onclick='viewpage(%d, %d)']" % (page, blogId))
        if len(nextpage) == 0:
            return False
        nextpage[0].click()
        time.sleep(3)
        return True

    def getCommentPersons(self, commentModule):
        '''
        Get the commenter for this article.
        '''
        commentPersons = commentModule.find_elements_by_xpath("dl/dt")
        persons = []
        for person in commentPersons:
            # print person.text
            #time.sleep(1)
            idModule = person.find_elements_by_xpath("a")
            if len(idModule) == 0:
                continue
            idModule = idModule[0]
            href = idModule.get_attribute("href")
            uidlist = self.pattern.findall(href)
            timeModule = person.find_element_by_xpath("span[@class='xg1 xw0']")
            if len(uidlist):
                person_id = int(uidlist[0])
                person_time = timeModule.text
                persons.append([person_id,person_time])
        return persons

def saveBlogPage(mCWebRender, mCSciencePage, url):
    ''''''
    mCSciencePage.getPage(url, mCWebRender)
    num = 0
    while True:
        title = mCSciencePage.getTitle(mCWebRender)
        num += 1
        if len(title) != 0 or num > 20:
            break
        else:
            time.sleep(30)
            mCSciencePage.getPage(url, mCWebRender)
    article = mCSciencePage.getContent(mCWebRender)
    article = article.translate(transtab)
    recPersons = mCSciencePage.getRecPersons(mCWebRender)
    commentPersons = mCSciencePage.getAllComments(mCWebRender)
    return title, article, recPersons, commentPersons

def getBlog(db, itemsNum):
    sql = 'select blog_id, blog_href from blogs where flag = 0 LIMIT %d ' %  itemsNum
    blogs = db.InquiryTb(sql)
    if len(blogs) == 0:
        return False, False
    sql = 'update blogs set flag = 1 where blog_id=%d' % blogs[0]['blog_id']
    db.UpdateTb(sql)
    return blogs[0]['blog_id'], blogs[0]['blog_href']


def main():
    db = connectDb()
    mCWebRender = CWebRender()
    mCSciencePage = CSciencePage()
    while True:
        blog_id, blog_href = getBlog(db, 1)
        if not blog_id: break
        print 'Blog ID: ', blog_id
        url = 'http://blog.sciencenet.cn/' + blog_href
        title, article, recPersons, commentPersons = saveBlogPage(mCWebRender, mCSciencePage, url)

        sql = 'update blogs set blog_title="%s", blog_content="%s", flag=2 where blog_id=%d '
        db.UpdateTb(sql % (title, article, blog_id))
        values = [(blog_id, person) for person in recPersons]
        sql = 'insert into recblogperson(blog_id, user_id) values(%s, %s)'
        db.InsertTb(sql, values)
        sql = 'insert into commentblogpersons(blog_id, user_id, time) values(%s, %s, %s)'
        values = [(blog_id, user_id, Time) for user_id, Time in commentPersons]
        db.InsertTb(sql, values)

    mCWebRender.closeUrl()
    db.CloseDb()
    
if __name__ == '__main__':
    main()
    #poolFunc(4, 10)


