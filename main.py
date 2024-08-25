import sys
from PyQt5.QtWidgets import QApplication
from file_system import FileSystem
from fat import FAT
from ui_elements import Block ,Catalog

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainform = FileSystem()
    mainform.show()
    sys.exit(app.exec_())
