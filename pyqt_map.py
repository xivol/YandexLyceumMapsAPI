import os
import sys

import requests
from PyQt5.Qt import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *

SCREEN_SIZE = [600, 450]


class YandexMapWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.needs_reload = True
        self.location = [37.530887, 55.703118]
        self.location_delta = 0.02
        self.layer = "map"
        self.current_org = None
        self.initUI()

    def getImage(self):
        map_request = "http://static-maps.yandex.ru/1.x/"

        map_params = {
            "ll": f"{self.location[0]},{self.location[1]}",
            "spn": f"{self.location_delta},{self.location_delta}",
            "l": self.layer
        }

        if self.current_org != None:
            map_params["pt"]=f"{self.current_org[2][0]},{self.current_org[2][1]},pm2dgl"
        response = requests.get(map_request, params=map_params)


        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

        self.search = QLineEdit(self)
        self.search.move(0, 450)
        self.search.resize(520, 20)

        self.searchButton = QPushButton("Искать", self)
        self.searchButton.move(520,450)
        self.searchButton.resize(80, 20)
        self.searchButton.clicked.connect(self.locate_point)


    def get_address(self):
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

        search_params = {
            "apikey": api_key,
            "text": self.search.text(),
            "lang": "ru_RU",
            "ll": f"{self.location[0]},{self.location[1]}",
            "type": "biz"
        }

        data = requests.get(search_api_server,search_params)
        json = data.json()

        # Получаем первую найденную организацию.
        organization = json["features"][0]
        # Название организации.
        name = organization["properties"]["CompanyMetaData"]["name"]
        # Адрес организации.
        address = organization["properties"]["CompanyMetaData"]["address"]

        # Получаем координаты ответа.
        point = organization["geometry"]["coordinates"]

        self.current_org = (name, address, point)

    def locate_point(self):
        self.get_address()
        self.location = self.current_org[2][:]
        self.needs_reload = True
        self.repaint()

    def paintEvent(self, event):
        if self.needs_reload:
            self.getImage()
            self.pixmap = QPixmap(self.map_file)
            self.image.setPixmap(self.pixmap)
            self.needs_reload = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.location_delta += 0.01
            self.needs_reload = True
        elif event.key() == Qt.Key_PageDown:
            self.location_delta -= 0.01
            self.needs_reload = True
        elif event.key() == Qt.Key_Up:
            self.location[1] += self.location_delta / 2
            self.needs_reload = True
        elif event.key() == Qt.Key_Down:
            self.location[1] -= self.location_delta / 2
            self.needs_reload = True
        self.repaint()

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YandexMapWidget()
    ex.show()
    sys.exit(app.exec())
