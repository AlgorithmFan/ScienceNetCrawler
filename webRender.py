from selenium import webdriver
from selenium.webdriver.common.proxy import *

class webRender(webdriver.Firefox):
    def __init__(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.proxy.type', 1)
        profile.set_preference('network.proxy.http', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        #profile.set_preference('network.proxy.http_port', 8080)
        profile.set_preference('network.proxy.ssl', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        #profile.set_preference('network.proxy.ssl_port', 8080)
        profile.update_preferences()
        webdriver.Firefox.__init__(self, profile)


    def loadSource(self, url, encoding='utf-8'):
        self.get(url)
        source = self.page_source
        return source

    def get_element_xpath(self, xpath):
        result = self.find_element_by_xpath(xpath)
        return result

    def get_element_class(self, value):
        result = self.find_element_by_class_name(value)
        return result

    def getPageTxt(self, url):
        self.get(url)
        text = list()
        pageNum = 1
        while True:
            try:
                element = self.find_element_by_id('pageNo-%d' % pageNum)
                text.append(element.text)
                pageNum = pageNum + 1
                element.click()
            except:
                print 'over %d' % pageNum
                return text
        return text

    def closeUrl(self):
        self.close()
        self.quit()

def main():
    url = 'http://wenku.baidu.com/view/7c9d96edb8f67c1cfad6b879.html'
    mWebRender = webRender()
    web = mWebRender.loadSource(url)
    result = mWebRender.get_element_class("inner")
    if result:
        print result

    result = mWebRender.getPageTxt(url)
    print len(result)
    mWebRender.closeUrl()

if __name__ == '__main__':
    main()


