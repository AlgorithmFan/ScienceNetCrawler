#!usr/bin/env python
#coding: utf-8
from CommonFunc import getUrlSource, connectDb
from Database import CDatabase
from lxml import etree
import re
Alphabets = 'ABCDEFGHIGKLMNOPQRSTUVWXYZ'

def getBloggers(letter):
    pattern = re.compile('&uid=(\d+)')
    url = 'http://blog.sciencenet.cn/blog.php?mod=member&alphabet=' + letter
    mSourceCode = getUrlSource(url)
    page = etree.HTML(mSourceCode)
    bloggerModules = page.xpath("//p[@class='potfont']")
    bloggers = set()
    for blogModule in bloggerModules:
        hrefs = blogModule.xpath("a")
        for href in hrefs:
            blogHref = href.attrib['href']
            blogger_id = pattern.findall(blogHref)
            if len(blogger_id):
                bloggers.add(int(int(blogger_id[0])))
    return bloggers

def getInformationBloggers():
    url = 'http://blog.sciencenet.cn/blog.php?mod=member&type=%BC%C6%CB%E3%BB%FA%D3%A6%D3%C3%BC%BC%CA%F5&realmmedium=%BC%C6%CB%E3%BB%FA%BF%C6%D1%A7&realm=%D0%C5%CF%A2%BF%C6%D1%A7&catid=528'
    pattern = re.compile('&uid=(\d+)')
    mSourceCode = getUrlSource(url)
    page = etree.HTML(mSourceCode)
    bloggerModules = page.xpath("//p[@class='potfont']")
    bloggers = set()
    for blogModule in bloggerModules:
        hrefs = blogModule.xpath("a")
        for href in hrefs:
            blogHref = href.attrib['href']
            blogger_id = pattern.findall(blogHref)
            if len(blogger_id):
                bloggers.add(int(int(blogger_id[0])))
    return bloggers

def getBlogs(url):
    '''
    Get the blogs href.
    '''
    hrefs = set()
    mSourceCode = getUrlSource(url)
    if len(mSourceCode) == 0:
        return hrefs
    page = etree.HTML(mSourceCode)
    bloggs = page.xpath("//dt[@class='xs2']")
    for blog in bloggs:
        tagA = blog.xpath('a')
        for a in tagA:
            if ('target' in a.attrib) and ('href' in a.attrib):
                hrefs.add(a.attrib['href'])
    return hrefs

def main():
    # bloggers = set()
    # for letter in Alphabets:
    #     temp = getBloggers(letter)
    #     bloggers |= temp
    # print 'Bloggers Number:', len(bloggers)

    bloggers = getInformationBloggers()
    url = 'http://blog.sciencenet.cn/home.php?mod=space&uid=%d&do=blog&view=me&from=space&page=%d'
    sql = 'insert into blogs(user_id, blog_href, flag) values(%s, %s, %s)'
    values = []
    db = connectDb()
    for blogger in bloggers:
        print 'user %d.' % blogger
        print 'values %d.' % len(values)
        for page in range(1000):
            temp = getBlogs(url % (blogger, page))
            if len(temp) == 0:
                break
            for href in temp:
                values.append((blogger, href, 0))
        if len(values) > 10000:
            db.InsertTb(sql, values)
            values = []

    db.InsertTb(sql, values)
    db.CloseDb()


if __name__=='__main__':
    main()
