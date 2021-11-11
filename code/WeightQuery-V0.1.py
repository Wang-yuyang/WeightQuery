import requests
import json
import re
import argparse
import sys
import os

class linkCleaning:
    '''
        :return : 返回一个清洗结果后的字符串（默认清洗其它字符，不清洗端口、协议、路径）
    '''
    def __init__(self, urls):
        '''
            :param urls: 传入单个含有链接的字符串，会清洗调与link无关的字符
        '''
        self.urls = urls
        self.delStr()
        # self.delHttp()
        # self.delPort()
        # self.delPath()
        # self.result()
    def delStr(self):
        # (re.search(r'(http[s]?://[^\s]+)', self.urls, re.I)).group()
        # (re.search(r'(((\w)*\.)+\w*)', urls)).group()
        self.urls = (re.search(r'((((\w)*\.)+\w*)|(http[s]?:\/\/[^\s]+))', self.urls, re.I)).group()

    def delHttp(self):
        self.urls = re.sub(r'(http[s]?:/*)', "", self.urls)

    def delPort(self):
        self.urls = re.sub(r'(:+[0-9]*)', "", self.urls)

    def delPath(self):
        self.urls = re.sub(r'/.*', "", self.urls)

    def isIpAddr(self):
        if len(re.findall(r'(^\d+.\d+.\d+.\d+)', self.urls))>0:
            return True
        else:
            return False

    def result(self):
        return self.urls


class getWeight:
    def __init__(self):
        self.domainList = []
        self.domainErrorList = []
        self.domainWeightList = []
        pass

    def linkExtract(self,urls):
        '''
        :function: 调用link清洗类，从字符串中提取一个合法的域名
        :return: 返回正确的一个域名字符串
        '''
        linkCleaningObj = linkCleaning(urls=urls)
        if linkCleaningObj.isIpAddr() :
            return False
        else:
            linkCleaningObj.delHttp()
            linkCleaningObj.delPath()
            linkCleaningObj.delPort()
            if linkCleaningObj.isIpAddr():
                # return False
                # URL最后提取发现属于一个IP地址，则返回为空字符
                print(linkCleaningObj.result())
                return False
            else:
                return linkCleaningObj.result()

    def domainListCheck(self, urlList):
        '''
        执行域名清洗提纯的操作（通过list迭代逐一清洗URL）
        domainListCheck() --> self.linkExtract() --> public class linkCleaning
        :param urlList: 源URL列表数据
        :return: True
        '''
        # print(urlList)
        for i in range(0, len(urlList)):
            urlStr = self.linkExtract(urlList[i])
            if urlStr != False :
                self.domainList.append(str(urlStr))
            else:
                self.domainErrorList.append(urlList[i])
                continue

        return True

    def weight_baidu_Api(self,urlStr):
        weight_url = "https://apistore.aizhan.com/baidurank/siteinfos/"+"9fca5f6917b893763b0d7f5063680794"
        param = {
            "domains": urlStr
        }
        res = requests.get(url=weight_url, params=param).text
        success_dict = json.loads(res)['data']['success']
        self.domainWeightList = self.domainWeightList + success_dict
        # for i in range(0, len(success_dict) - 1):
        #     print(success_dict[i]['domain'] + "|" + str(success_dict[i]['pc_br']))


    def domainGetWeight_Bidu(self,urlList):
        # print(len(urlList))
        # ① 启用URL域名清洗流程
        try:
            if self.domainListCheck(urlList) :
                print("\033[0;32m[SUCCESS]\033[0m 已完成[%d/%d]个域名清洗(执行去杂)"%(len(self.domainList),len(urlList)))
                self.domainList = list(dict.fromkeys(self.domainList))
                print("\033[0;32m[SUCCESS]\033[0m 已完成[%d/%d]个域名清洗(执行去重)"%(len(self.domainList),len(urlList)))
        except Exception as err:
            print("\033[0;31m[ERROR]\033[0m 域名清洗发生意料之外的错误" )
        # ② 将清洗后的域名列表进行合并查询权重
        try:
            for i in range(0, len(self.domainList), 50):
                result = urlList_str = "|".join(self.domainList[i:i+50])
                # print(result)
                self.weight_baidu_Api(urlList_str)
                print("\033[0;32m[错误域名]\033[0m"+str(self.domainErrorList))
                # print(self.domainWeightList)

                return self.domainWeightList
        except:
            print("\033[0;31m[ERROR]\033[0m 权重查询调用过程中发生意料之外的错误" )

# 导出文件
class exportFile:
    def __init__(self):
        pass

if __name__ == '__main__':
    print("欢迎使用基于爱站网的百度权重查询脚本")
    print('''
-----------------------------------------------------------------------
__        __   _       _     _      ___                        
\ \      / /__(_) __ _| |__ | |_   / _ \ _   _  ___ _ __ _   _ 
 \ \ /\ / / _ \ |/ _` | '_ \| __| | | | | | | |/ _ \ '__| | | |
  \ V  V /  __/ | (_| | | | | |_  | |_| | |_| |  __/ |  | |_| |
   \_/\_/ \___|_|\__, |_| |_|\__|  \__\_\\__,_|\___|_|   \__, |
                 |___/                                   |___/ 
                     Author : Mirror
                    Version : V0.1 (2021/11/11)
                  statement : 禁止用于未授权测试，仅供安全研究使用。
-----------------------------------------------------------------------
***************************** Update log ******************************
[20211111](V0.1)--发布WeightQuery，具备批量权重查询和单域名权重查询的基本功能。 
***********************************************************************
    ''')

    parser = argparse.ArgumentParser(description="..")
    parser.add_argument('-f', type=str, help="需要导入查询权重的URL文件")
    parser.add_argument('-o', type=str, help="导出查询结果的相对位置(文件名自动生成)")
    parser.add_argument('-u', type=str, help="需要查询权重的URL(单个)")
    args = parser.parse_args()
    try:
        if args.f:
            files = open(args.f, mode='r')
            url_list = files.read().splitlines()
            result = getWeight().domainGetWeight_Bidu(url_list)
            files.close()
            f = open('./url_weight.json', mode='w')
            f.write(json.dumps(result))
            f.close()
        elif args.u:
            urls = []
            urls.append(str(args.u))
            result = getWeight().domainGetWeight_Bidu(urls)
            print("\033[0;32m权重查询结果 %s ==> 【%s】\033[0m" % (str(result[0]['domain']), str(result[0]['pc_br'])))
    finally:
        while True:
            urls = []
            urls.append(input("\033[0;32m需要查询权重的URL(单个) : \033[0m"))
            result = getWeight().domainGetWeight_Bidu(urls)
            print("\033[0;32m权重查询结果 %s ==> 【%s】\033[0m" % (str(result[0]['domain']), str(result[0]['pc_br'])))

    input()