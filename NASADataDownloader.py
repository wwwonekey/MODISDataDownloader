'''/*
 * @Author: wk 
 * @Date: 2018-09-28 16:44:16 
 * @Last Modified by: wk
 * @Last Modified time: 2018-09-28 16:44:48
 */'''
#D:\python3.7
# -*- coding:utf-8 -*-

import urllib.request,json,os,subprocess,time,sys
# import wget

# NASA数据地址
mainUrl = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/6"

# productName = ""
# yearList = []



# 读取NASA网页中json的信息
def ReadJsonProductName(url):
    json = ".json"
    url = url + json
    name = GetProductNameFromWebPage(url)
    if name: #name不为空，说明有数据，返回数据
        # print(name)
        return name
    return False  #name 为空，返回错误


def ConnectWebPage(url):
    headers = {
    #伪装为浏览器抓取
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    req = urllib.request.Request(url,headers=headers)
    try:
        fdata = (urllib.request.urlopen(req,timeout=10)).read()
        return fdata
    except IOError:
        print("爬取网页超时，正在重试！")
        time.sleep(10)
        # f = urllib.request.urlopen(req,timeout=10) 
        fdata = ConnectWebPage(url)
        return fdata

def GetProductNameFromWebPage(url):
    fdata = ConnectWebPage(url)
    if fdata:#如果f不为空的话，说明网页读取成功了，那么我们就可以去处理它了
        # readdata = f.read()
        try:
            # data = json.loads(fdata) #字符串转换成字典
            data = json.loads(fdata)#字符串转换成字典
            name = GetProductName(data)
            return name
        except:
            data = json.loads(fdata)#字符串转换成字典
            name = GetProductName(data)
            return name
    else:
        print("网页打不开！")

# 动态创建字典，便于提取产品名称
def GetProductName(data):
    """
    docstring 获取产品名称，并以产品名称作为key-value中key和value，返回字典
        :param data: 字典数据
    """
    nameDict = {}
    for i in data:
        nameDict[i.get("name")] = i.get("name")
        # nameDict[str(i.get("name"))] = i.get("name")
    return nameDict
    

def GetProductData(url,product,years,julianDays,colrowIndexs,outPath):
    """
    docstring here
        :param url: 路径
        :param product: 产品名称
        :param years: 需要下载的年份，可以是多年
        :param colrowIndexs: 行号h,带号v,存放行代号的数组
    """
    urlPath =sys.path[0] +"\\" +"url.txt"
    urlFile = open(urlPath, 'w')
    productUrl = url +"/"+ product
    fileYears = ReadJsonProductName(productUrl)
    
    log = open("log.txt", 'w')

    fileNum = 0

    if(fileYears):
        for year in years:
            # 产品加所需数据年份路径
            productYearUrl = productUrl + "/" + fileYears[str(year)]
            juliandayName = ReadJsonProductName(productYearUrl)

            # 循环拿到的儒略日时间，如果该时间在所需要的时间内则进行下一步，否则继续，知道循环完毕
            for dayName in juliandayName:
                if(julianDays[0] <= int(dayName) <=julianDays[1]):
                    # print(julianDays[0])
                    productYearJulianDaysUrl = productYearUrl + "/" + dayName
                    fileNames = ReadJsonProductName(productYearJulianDaysUrl)
                    for file in fileNames:
                        # 数据最终路径
                        dataUrl = productYearJulianDaysUrl +"/" +file
                        if(len(file.split('.')[2]) == 6): #长度为6说明有条带号
                            col = int(file.split('.')[2][1:3])
                            row = int(file.split('.')[2][4:])
                            for hvIndex in colrowIndexs:
                                if(col == hvIndex[0] and row == hvIndex[1]):
                                    print(file)
                                    fileNum += 1
                                    # 写出需要下载的数据
                                    urlFile.writelines(dataUrl+"\n")
                                    DownLoadFiles(dataUrl,"-q",outPath,file,log)
                                else:
                                    continue
                        elif (len(file.split('.')[2]) == 4):#长度为4说明另一种形式
                            pass
    else:
        print("该产品没有数据！")
    # i 
    urlFile.close()
    print("数据下载完成，共下载"+str(fileNum)+"景！")
    # DownLoadFiles(urlPath,"-i",outPath,file,log)
    log.close()
    
    
    # DownLoadFiles(urlPath)

def DownLoadFiles(urlPath,option,outpath,filename,log):
    """
    docstring 调用wget下载数据
        :param urlPath: 下载数据的网址
        :param option: wget的下载命令，p表示静默下载，i表示批量下载文本中的文件地址数据
        :param outpath: 输出路径
        :param filename: 下载文件的名字
        :param log: 下载日志
    """
    cmdWget = 'wget '+str(option)+" "+urlPath
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    try:
        os.chdir(outpath)
        status = subprocess.call(cmdWget,shell=True)
        if status !=0:
            log.write('\nFailed:'+filename)
        log.write('\nSuccess:'+filename)
        log.flush()
    except:
        log.write('\nFailed:'+filename)



if __name__ == "__main__":
    yearlist = [2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016]
    julianDays = [1,1] #第一个为开始日期，第二个为结束日期
    hvs =[[0,8],[16,9],[32,12]]
    outpath = "E:\code\python\caa"
    GetProductData(mainUrl,"MOD13Q1",yearlist,julianDays,hvs,outpath)