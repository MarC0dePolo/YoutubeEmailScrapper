from getEmails import Crawler
import multiprocessing
import time
import sys

class TurboCrawler(Crawler):
    def __init__(self) -> None:
        super().__init__()

    def getProcAmount(self):
        self.numProc = int(input("How many Processes?: "))
        if self.numProc > 10:
            print("MAX = 10")
            sys.exit(0)

    def splitQuery(self):
        content = self.readQuery()
        numLines = len(content)
        
        numOfQueryInEachFile = numLines // self.numProc
        numOfRemainingQuerys = numLines % self.numProc
        
        startIndex = 0
        for i in range(self.numProc):
            with open(f"data/multiQuerys/tmpQuery{i}.txt", "+a") as file:
                for j in content[startIndex:startIndex+numOfQueryInEachFile]:
                    file.write(j+"\n")
            
            startIndex += numOfQueryInEachFile
            
            if startIndex == numLines - numOfRemainingQuerys:
                break    
        
        if numOfRemainingQuerys > 0:
            remainingItems = content[-(numOfRemainingQuerys):]
            count = 0
            for i in remainingItems:
                if count > self.numProc -1:
                    count = 0
                with open(f"data/multiQuerys/tmpQuery{count}.txt", "+a") as file:
                    file.write(i+"\n")
                count += 1
    
    def startProcesses(self):
        processes = []
        for num in range(self.numProc):
            crawler = Crawler()
            process = multiprocessing.Process(target=crawler.main, args=(num, self.numProc))
            process.start()
            processes.append(process)
            time.sleep(15)

        for process in processes:
            process.join()

    def main(self):
        self.getProcAmount()
        self.splitQuery()
        self.startProcesses()

if __name__ == "__main__":
    turboCrawler = TurboCrawler()
    turboCrawler.main()