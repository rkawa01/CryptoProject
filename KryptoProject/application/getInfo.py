from PyQt5 import QtCore, QtNetwork

import json
class JsonInfo():
    def __init__(self,username=None,password=None):
        self.username = username
        self.password = password
        self.bit = None
        self.token = None
        self.wallet = None
        self.manager = QtNetwork.QNetworkAccessManager()
        self.info = ''
        self.loop = QtCore.QEventLoop()
        self.manager.finished.connect(self.handleDone)
    def setter(self,bit,wallet):
        self.bit = bit
        self.wallet = wallet
    def postresponse(self,flag = True):
        if flag:
            self.url = QtCore.QUrl('http://127.0.0.1:8000/crypto/login/')
            params = {"name": self.username, "pass": self.password}
        else:
            self.url = QtCore.QUrl('http://127.0.0.1:8000/crypto/index/')
            params = {"bit":str(self.bit),"wallet":str(self.wallet)}
        request = QtNetwork.QNetworkRequest(self.url)
        if (self.token is not None):
            print("GO")
            print(self.token)
            request.setRawHeader(b"X-CSRFToken", self.token.encode())
        multi_part = self.construct_multipart(params)
        self.reply = self.manager.post(request,multi_part)
        multi_part.setParent(self.reply)

        self.loop.exec_()
    def getresponse(self):
        self.url = QtCore.QUrl('http://127.0.0.1:8000/crypto/index/')
        request = QtNetwork.QNetworkRequest(self.url)
        self.reply = self.manager.get(request)
        self.loop.exec_()

    def handleDone(self):
        self.loop.quit()
        # print(self.reply.readAll().data())
        data_get = self.reply.readAll().data()
        # print(data_get)
        # print(data_get)
        # responseData = {'message':None}
        # print("load")
        # print(data_get)
        if(data_get != b''):
            responseData = json.loads(data_get)
            self.info = responseData
            # print(self.info)
        else:
            self.info = None

        if self.reply.error() == QtNetwork.QNetworkReply.NoError:

            print('Success')

        else:
            print('Error')
    def settoken(self,token):
        self.token = token

    def construct_multipart(self, data):
        multi_part = QtNetwork.QHttpMultiPart(QtNetwork.QHttpMultiPart.FormDataType)
        for key, value in data.items():
            post_part = QtNetwork.QHttpPart()
            post_part.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader,
                                "form-data; name=\"{}\"".format(key))
            post_part.setBody(str(value).encode())
            multi_part.append(post_part)

        return multi_part
