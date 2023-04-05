from PyQt5 import QtCore, QtNetwork

import json
class JsonInfo():
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.url = 'http://127.0.0.1:8000/crypto/'
        self.userAgent = b'Application admin'
        self.manager = QtNetwork.QNetworkAccessManager()
        self.info = ''
        self.getresponse()
        
    def getresponse(self):
        self.loop = QtCore.QEventLoop()
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(self.url))

        params = {"name": self.username, "pass": self.password}
        multi_part =self.construct_multipart(params)
        self.reply = self.manager.post(request,multi_part)
        multi_part.setParent(self.reply)
        self.manager.finished.connect(self.handleDone)
        self.loop.exec_()


    def handleDone(self):
        self.loop.quit()
        responseData = json.loads(self.reply.readAll().data())

        if self.reply.error() == QtNetwork.QNetworkReply.NoError:
            print('Success')
        else:
            print('Error')

        self.info = responseData['message']

    def construct_multipart(self, data):
        multi_part = QtNetwork.QHttpMultiPart(QtNetwork.QHttpMultiPart.FormDataType)
        for key, value in data.items():
            post_part = QtNetwork.QHttpPart()
            post_part.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader,
                                "form-data; name=\"{}\"".format(key))
            post_part.setBody(str(value).encode())
            multi_part.append(post_part)

        return multi_part
