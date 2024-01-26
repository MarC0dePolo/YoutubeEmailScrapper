from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import regex as re
import multiprocessing
import sys

class Crawler:
    def __init__(self) -> None:
        self.chromedriverPath = "/usr/bin/chromedriver"
        self.youtube_cookies_button = '//*[@id="content"]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button'
        #self.youtube_open_filter_button = '//*[@id="container"]/ytd-toggle-button-renderer/yt-button-shape/button'
        self.youtube_open_filter_button = '//*[@id="filter-button"]/ytd-button-renderer/yt-button-shape/button'
        self.youtube_filter_group = "/html/body/ytd-app/ytd-popup-container/tp-yt-paper-dialog/ytd-search-filter-options-dialog-renderer/div[2]/ytd-search-filter-group-renderer[1]"
        
        self.pathToUsedLinks = "data/usedLinks.txt"
        self.pathToMultiQuerys = "data/multiQuerys"
        self.pathToEmails = "data/emails.txt"
        self.pathToBlacklist = "data/blacklist.txt"
        
        self.lock = multiprocessing.Lock()
        
        self.links =  []
        self.waitLong = 5
        self.waitMid = 2
        self.waitShort = 1
        
        self.emailsAlreadyKnown = 0
        self.newEmailsFound = 0
        
        #self.timeFrame = sys.argv[1]
        self.timeFrame = "thisYear"
        #self.querysTxt = sys.argv[2]
        self.querysTxt = "data/nowQuerys.txt"
        
        #self.querys = self.readQuery()
        self.usedLinks = self.saveUsedLinksRead()
        self.blacklist = self.saveBlacklistRead()
        
        self.emails = self.saveEmailRead()

    #Read list of Emails that should not be saved
    def saveBlacklistRead(self):
        with self.lock:
            with open(self.pathToBlacklist, "r") as file:
                self.blacklist = file.read().strip().split("\n")
            
            return self.blacklist

    def saveEmailRead(self):
        with self.lock:
            with open(self.pathToEmails , "r") as file:
                self.emails = file.read().strip().split("\n")
            return self.emails
    
    def saveEmailWrite(self, email):
        with self.lock:
            with open(self.pathToEmails, "a") as file:
                file.write(email+"\n")
                
    def saveOutputWrite(self, msg):
        with self.lock:
            with open("data/output.txt", "a") as file:
                file.write(f'\nprocess: {self.process}\n{msg}\n')
    
    def usedLinkToTxt(self, link):
        with self.lock:
            with open(self.pathToUsedLinks, "a") as file:
                file.write(link+"\n")    
    
    def getLength(self):
        return len(self.emails)

    def saveUsedLinksRead(self):
        with self.lock:
            with open(self.pathToUsedLinks, "r") as file:
                data = file.read().strip().split("\n")
            return data
        
        # Start Chromium
        self.driver = webdriver.Chrome()
        self.driver.set_window_position(2500,0)
        self.driver.get(f"https://www.youtube.com")
        time.sleep(self.waitMid)
        for i in range(3):
        # Find Cookies Button and click
            time.sleep(self.waitLong)
            try:  
                l = self.driver.find_element(By.XPATH, self.youtube_cookies_button)
                l.click()
                break
            except Exception as error:
                self.saveOutputWrite(msg=f"{error}")   
                     
        if i == 2:
            self.saveOutputWrite(msg=f"EXITED PROCESS DUE TO FAILURE OF CLICKING COOKIES")
            sys.exit(0)
            
        time.sleep(self.waitMid)
        self.driver.set_window_size(495, 540)
        time.sleep(self.waitMid)
        self.driver.execute_script("document.body.style.zoom='65%';")
        time.sleep(self.waitMid)
        self.driver.set_window_position(x_y_coordinates[str(self.process)][0], x_y_coordinates[str(self.process)][1])
        time.sleep(self.waitMid)
        
        with self.lock:
            with open("data/output.txt", "a") as file:
                file.write(f"\nprocess: {self.process}\nINIT COMPLETE!\n")

    ### Filter Videos by time ###
    def thisDay(self):
        button = self.driver.find_element(By.XPATH, self.youtube_filter_group+'/ytd-search-filter-renderer[2]/a')
        link = button.get_attribute("href")
        
        return link
    def thisWeek(self):
        button = self.driver.find_element(By.XPATH, self.youtube_filter_group+'/ytd-search-filter-renderer[3]/a')
        link = button.get_attribute("href")
        return link
        
    def thisMonth(self):
        button = self.driver.find_element(By.XPATH, self.youtube_filter_group+'/ytd-search-filter-renderer[4]/a')
        link = button.get_attribute("href")
        return link
        
    def thisYear(self):
        button = self.driver.find_element(By.XPATH, self.youtube_filter_group+'/ytd-search-filter-renderer[5]/a')
        link = button.get_attribute("href")
        return link

    #Scroll to Bottom
    def loadFullPage(self):
        
        previousPos = None
        currentPos = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
        
        while True:
            self.driver.execute_script("window.scrollBy(0,10000)","")
            time.sleep(self.waitMid)
            previousPos = currentPos
            currentPos = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
            if previousPos == currentPos:
                break
        
        self.saveOutputWrite(msg="SCROLLED TO BOTTOM")
    
    def getYoutubeLinks(self, query, timeFrameMethod):
        # List Videos with youtube Query
        self.driver.get(f"https://www.youtube.com/results?search_query={query}")
        time.sleep(self.waitLong)
        
        # open Filter Group
        filter = self.driver.find_element(By.XPATH, self.youtube_open_filter_button)
        filter.click()
        time.sleep(self.waitMid)
        
        self.driver.get(timeFrameMethod())
        time.sleep(self.waitLong)
        self.loadFullPage()
        videos = self.driver.find_elements(By.ID, 'video-title')
            
        # filter the output by href
        newFound = 0
        oldFound = 0
        
        for video in videos:
            link = video.get_attribute("href")
            if (link != None) and ("shorts" not in link) and (link not in self.usedLinks):
                self.links.append(link)
                newFound += 1
                #print(f"NEW! {link}")
                
            else:
                oldFound += 1
                #print(f"OLD!{link}")
        self.saveOutputWrite(msg=f"NEW: {newFound}\nOLD: {oldFound}")

        newFound = 0
        oldFound = 0
        
    def getEmailFromVideoPage(self, videoPage):
        self.driver.get(videoPage)
        time.sleep(self.waitLong)
        
        #expand discription
        showMore = self.driver.find_element(By.XPATH, '//*[@id="expand"]')
        showMore.click()
        
        time.sleep(self.waitMid)
        
        description = self.driver.find_element(By.XPATH, '//*[@id="description-inner"]')
        description = description.get_attribute("innerHTML")
        description = BeautifulSoup(description, "html.parser")
        description = description.find_all("span")

        # Search Email by regex
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for span in description:
            emailList = re.findall(regex, span.text)
            
            # search will always make it in a list also if just one element found
            if emailList != []:
                self.emailsToExcel(emailList)
                break
            
        if emailList == []:
            self.saveOutputWrite(msg=f"NO EMAIL FOUND IN:\n{videoPage}")
                
        self.usedLinks.append(videoPage)
        self.usedLinkToTxt(link=videoPage)
        self.usedLinks = self.saveUsedLinksRead()
    
    def emailsToExcel(self, emails):
        # Put email in excel and save it
        for email in emails:
            if (email not in self.emails) and (email not in self.blacklist):
                
                self.emails.append(email)
                self.saveEmailWrite(email=email)
                self.emails = self.saveEmailRead()
                
                self.saveOutputWrite(msg=f"+++++\n+++++ {email}\n+++++")
            
            else:
                self.saveOutputWrite(msg=f"----- {email}")

    def readQuery(self):
        with self.lock:
            with open(self.querysTxt, "r") as file:
                content = file.read().strip().split("\n")
        return content


    def readSplitedQuery(self, num):
        with self.lock:
            with open(f"{self.pathToMultiQuerys}/tmpQuery{num}.txt", "r") as file:
                content = file.read().strip().split("\n")
        return content

    def main(self, num1, num2):
        
        self.process = num1
        self.numOfProcesses = num2
        
        querys = self.readSplitedQuery(num1)
        
        self.initYoutube()
        
        timeFrameMethods = {
            "thisDay": self.thisDay,
            "thisWeek": self.thisWeek,
            "thisMonth": self.thisMonth,
            "thisYear": self.thisYear,
        }
        for query in querys:
            self.saveOutputWrite(msg=f"Starting with: {query}") 
            
            timeFrameMethod = timeFrameMethods[self.timeFrame]

            for i in range(15):
                time.sleep(self.waitLong)
                try:
                    self.getYoutubeLinks(query, timeFrameMethod=timeFrameMethod)
                    break
                except Exception as error:
                    self.saveOutputWrite(msg=f"{error}")
                    continue
            
            if i == 14:
                self.saveOutputWrite(msg=f"EXITED PROCESS DUE TO FAILURE OF [self.getYoutubeLinks()]")
                sys.exit(0)    
            
            counter = 0
            for videoPage in self.links:
                counter += 1
                if videoPage not in self.usedLinks:
                    #print(f"\n#{counter} CRAWLING!: {videoPage}")
                    try:
                        self.getEmailFromVideoPage(videoPage=videoPage)

                    except Exception as error:
                        
                        continue
            
            self.links = []

        self.driver.close()

if __name__ == "__main__":
    crawler = Crawler()
    crawler.main(1, 1)
