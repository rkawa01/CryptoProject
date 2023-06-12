from PyQt5 import QtCore, QtNetwork

import json
class JsonInfo():
    def __init__(self):
        self.token = None
        self.manager = QtNetwork.QNetworkAccessManager()
        self.info = ''
        self.loop = QtCore.QEventLoop()
        self.manager.finished.connect(self.handleDone)

    def postResponse(self, url, params):
        self.url = QtCore.QUrl(url)
        request = QtNetwork.QNetworkRequest(self.url)
        if (self.token is not None):
            request.setRawHeader(b"X-CSRFToken", self.token.encode())
        multi_part = self.construct_multipart(params)
        self.reply = self.manager.post(request,multi_part)
        multi_part.setParent(self.reply)

        self.loop.exec_()
    def getResponse(self):
        self.url = QtCore.QUrl('http://127.0.0.1:8000/crypto/index/')
        request = QtNetwork.QNetworkRequest(self.url)
        if (self.token is not None):
            request.setRawHeader(b"X-CSRFToken", self.token.encode())
        self.reply = self.manager.get(request)
        self.loop.exec_()

    def handleDone(self):
        self.loop.quit()
        data_get = self.reply.readAll().data()

        if(data_get != b''):
            responseData = json.loads(data_get)
            self.info = responseData
        else:
            self.info = None

        if self.reply.error() == QtNetwork.QNetworkReply.NoError:
            print('Success')
        else:
            print('Error')
    def setToken(self,token):
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
