__author__ = 'https://github.com/rkawa01/CryptoProject'
__copyright__ = 'Copyright (c) 2023'
__version__ = '1.0.0'
from PyQt6 import QtCore, QtNetwork

import json

class JsonInfo:
    def __init__(self):
        self.reply = None
        self.url = None
        self.token = None
        self.manager = QtNetwork.QNetworkAccessManager()
        self.info = ''
        self.loop = QtCore.QEventLoop()
        self.manager.finished.connect(self.handle_done)

    def post_response(self, url, params):
        self.url = QtCore.QUrl(url)
        request = QtNetwork.QNetworkRequest(self.url)
        if self.token is not None:
            request.setRawHeader(b"X-CSRFToken", self.token.encode())
        multi_part = self.construct_multipart(params)
        self.reply = self.manager.post(request, multi_part)
        multi_part.setParent(self.reply)
        self.loop.exec()

    def get_response(self):
        self.url = QtCore.QUrl('http://127.0.0.1:8000/crypto/index/')
        request = QtNetwork.QNetworkRequest(self.url)
        if self.token is not None:
            request.setRawHeader(b"X-CSRFToken", self.token.encode())
        self.reply = self.manager.get(request)
        self.loop.exec()

    def handle_done(self):
        self.loop.quit()
        data_get = self.reply.readAll().data()

        if data_get != b'':
            response_data = json.loads(data_get)
            self.info = response_data
        else:
            self.info = None

        if self.reply.error() == QtNetwork.QNetworkReply.NetworkError.NoError:
            print('Success')
        else:
            print('Error')

    def set_token(self, token):
        self.token = token

    @staticmethod
    def construct_multipart(data):
        multi_part = QtNetwork.QHttpMultiPart(QtNetwork.QHttpMultiPart.ContentType.FormDataType)
        for key, value in data.items():
            post_part = QtNetwork.QHttpPart()
            post_part.setHeader(QtNetwork.QNetworkRequest.KnownHeaders.ContentDispositionHeader,
                                "form-data; name=\"{}\"".format(key))
            post_part.setBody(str(value).encode())
            multi_part.append(post_part)

        return multi_part
