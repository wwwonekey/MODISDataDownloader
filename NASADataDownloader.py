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
from io import StringIO
# from pathlib import Path
# NASA数据地址
mainUrl = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/6"

# productName = ""
# yearList = []
USERAGENT = 'tis/download.py_1.0--' + sys.version.replace('\n','').replace('\r','')
def geturl(url, token="2DEE8672-6F03-11EA-B6AF-B772F64958BC", out=None):
    headers = { 'user-agent' : USERAGENT }
    if not token is None:
        headers['Authorization'] = 'Bearer ' + token
    try:
        import ssl
        CTX = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        if sys.version_info.major == 2:
            import urllib2
            try:
                fh = urllib2.urlopen(urllib2.Request(url, headers=headers), context=CTX)
                if out is None:
                    return fh.read()
                else:
                    shutil.copyfileobj(fh, out)
            except urllib2.HTTPError as e:
                print('HTTP GET error code: %d' % e.code(), file=sys.stderr)
                print('HTTP GET error message: %s' % e.message, file=sys.stderr)
            except urllib2.URLError as e:
                print('Failed to make request: %s' % e.reason, file=sys.stderr)
            return None

        else:
            from urllib.request import urlopen, Request, URLError, HTTPError
            try:
                fh = urlopen(Request(url, headers=headers), context=CTX)
                if out is None:
                    return fh.read().decode('utf-8')
                else:
                    shutil.copyfileobj(fh, out)
            except HTTPError as e:
                print("http请求失败，等待10秒")
                time.sleep(10)
                geturl(url, token="2DEE8672-6F03-11EA-B6AF-B772F64958BC")
                # print('HTTP GET error code: %d' % e.code(), file=sys.stderr)
                # print('HTTP GET error message: %s' % e.message, file=sys.stderr)
            except URLError as e:
                print('Failed to make request: %s' % e.reason, file=sys.stderr)
            return None

    except AttributeError:
        # OS X Python 2 and 3 don't support tlsv1.1+ therefore... curl
        import subprocess
        try:
            args = ['curl', '--fail', '-sS', '-L', '--get', url]
            for (k,v) in headers.items():
                args.extend(['-H', ': '.join([k, v])])
            if out is None:
                # python3's subprocess.check_output returns stdout as a byte string
                result = subprocess.check_output(args)
                return result.decode('utf-8') if isinstance(result, bytes) else result
            else:
                subprocess.call(args, stdout=out)
        except subprocess.CalledProcessError as e:
            print('curl GET error message: %' + (e.message if hasattr(e, 'message') else e.output), file=sys.stderr)
        return None





# 读取NASA网页中json的信息
def ReadJsonProductName(url):
    name = GetProductNameFromWebPage(url)
    if name: #name不为空，说明有数据，返回数据
        # print(name)
        return name
    return False  #name 为空，返回错误


def GetProductNameFromWebPage(url):
    # fdata = ConnectWebPage(url)
    # fdata = ReadJsonProductName(url)
    fdata = ""
    i= 1
    while not fdata:
        try:
            import csv
            fdata = [ f for f in csv.DictReader(StringIO(geturl('%s.csv' % url)), skipinitialspace=True) ]
            print("第"+str(i)+"次，获取数据")
            i = i+1
        except ImportError:
            import json
            fdata = json.loads(geturl(url + '.json'))
            time.sleep(10)
            print("第"+str(i)+"次，获取数据")
            i = i+1

    if fdata:#如果f不为空的话，说明网页读取成功了，那么我们就可以去处理它了
        # readdata = f.read()
        try:
            # data = json.loads(fdata) #字符串转换成字典
            # data = json.loads(fdata)#字符串转换成字典
            name = GetProductName(fdata)
            return name
        except:
            # data = json.loads(fdata)#字符串转换成字典
            name = GetProductName(fdata)
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

    # if os.path.exists(urlPath):
    #     os.remove(urlPath)

    productUrl = url +"/"+ product
    fileYears = GetProductNameFromWebPage(productUrl)
    
    log = open("log.txt", 'w')

    fileNum = 0

    if(fileYears):
        for year in years:
            # 产品加所需数据年份路径
            productYearUrl = productUrl + "/" + fileYears[str(year)]
            juliandayName = ReadJsonProductName(productYearUrl)
            # 循环拿到的儒略日时间，如果该时间在所需要的时间内则进行下一步，否则继续，知道循环完毕
            for dayName in juliandayName:
                # urlFile = open(urlPath, 'a')
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
                                    # DownLoadFiles(dataUrl,"-q",outPath,file,log)
                                else:
                                    continue
                        elif (len(file.split('.')[2]) == 4):#长度为4说明另一种形式
                            pass
                # urlFile.close()
    else:
        print("该产品没有数据！")
    #
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
    yearlist = [2020]
    julianDays = [1,59] #第一个为开始日期，第二个为结束日期
    hvs =[[25,3],[26,3],[23,4],[24,4],[25,4],[26,4],[27,4],[23,5],[24,5],[25,5],[26,5],[27,5],[28,5],[25,6],[26,6],[27,6],[28,6],[29,6],[28,7],[29,7]]
    outpath = "E:\code\python\caa"
    GetProductData(mainUrl,"MCD19A2",yearlist,julianDays,hvs,outpath)