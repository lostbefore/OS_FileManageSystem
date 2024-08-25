import sys
from typing import Optional
import PyQt5
from PyQt5.QtCore import QSize
from PyQt5.Qt import *
import time
import os
import pickle
blockSize = 512
blockNum = 512

class Block:
    def __init__(self, blockIndex: int, data=""):
        self.blockIndex = blockIndex
        self.data = data

    def write(self, newData: str):
        self.data = newData[:blockSize]
        return newData[blockSize:]

    def read(self):
        return self.data

    def isFull(self):
        return len(self.data) == blockSize

    def append(self, newData: str) -> str:
        remainSpace = blockSize - len(self.data)
        if remainSpace >= len(newData):
            self.data += newData
            return ""
        else:
            self.data += newData[:remainSpace]
            return newData[remainSpace:]

    def clear(self):
        self.data = ""

class FCB:

    def __init__(self, name, createTime, data, fat, disk):
        self.name = name
        self.createTime = createTime
        self.updateTime = self.createTime
        self.start = -1

    def update(self, newData, fat, disk):
        self.start = fat.update(self.start, newData, disk)

    def delete(self, fat, disk):
        fat.delete(self.start, disk)

    def read(self, fat, disk):
        if self.start == -1:
            return ""
        else:
            return fat.read(self.start, disk)


class Catalog:

    def __init__(self, name, isFile, fat, disk, createTime, parent=None, data=""):       
        self.name = name      
        self.isFile = isFile       
        self.parent = parent
        self.createTime = createTime
        self.updateTime = createTime
        if not self.isFile:
            self.children = []
        else:
            self.data = FCB(name, createTime, data, fat, disk)



class EditingInterface(QWidget):
    _signal = PyQt5.QtCore.pyqtSignal(str)

    def __init__(self, name, data):
        super().__init__()
        self.resize(1200, 800)
        self.setWindowTitle(name)
        self.name = name
        self.setWindowIcon(QIcon('img/file.png'))
        self.resize(412, 412)
        self.text_edit = QTextEdit(self)  
        self.text_edit.setText(data) 
        self.text_edit.setPlaceholderText("在此输入文件内容")  
        self.text_edit.textChanged.connect(self.changeMessage) 
        self.initialData = data
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.text_edit)
        self.v_layout.addLayout(self.h_layout)
        self.setLayout(self.v_layout)
        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
    
    def closeEvent(self, event):
       
        if self.initialData == self.text_edit.toPlainText():
            event.accept()
            return

        reply = QMessageBox()
        reply.setWindowTitle('提醒')
        reply.setIcon(QMessageBox.Warning)
        reply.setWindowIcon(QIcon("img/folder.png"))
        reply.setText('您想将其保存到 "' + self.name + '" 吗？')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('保存')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('不保存')
        buttonI = reply.button(QMessageBox.Ignore)
        buttonI.setText('取消')

        reply.exec_()

        if reply.clickedButton() == buttonI:
            event.ignore()
        elif reply.clickedButton() == buttonY:
            self._signal.emit(self.text_edit.toPlainText())
            event.accept()
        else:
            event.accept()

    def changeMessage(self):
        pass

    def button_slot(self, button):
        if button == self.save_button:
            choice = QMessageBox.question(self, "Question", "Do you want to save it?", QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                with open('First text.txt', 'w') as f:
                    f.write(self.text_edit.toPlainText())
                self.close()
            elif choice == QMessageBox.No:
                self.close()
        elif button == self.clear_button:
            self.text_edit.clear()



class AttributeInterface(QWidget):
    def __init__(self, name, isFile, createTime, updateTime, child=0):
        super().__init__()
        self.setWindowTitle('属性')
        self.setWindowIcon(QIcon('img/attribute.png'))

        self.tabs = QTabWidget(self)

        self.tab = QWidget()
        self.tabs.addTab(self.tab, "详细信息")

        self.tab.layout = QFormLayout(self)

        name_icon = QLabel()
        name_label = QLabel(name)
        if isFile:
            pixmap = QPixmap('img/file.png')
        else:
            pixmap = QPixmap('img/folder.png')

       
        scaled_pixmap = pixmap.scaled(72, 72, Qt.KeepAspectRatio)
        name_icon.setPixmap(scaled_pixmap)

       
        name_layout = QHBoxLayout()
        name_layout.addWidget(name_icon)
        name_layout.addWidget(name_label)
        name_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.tab.layout.addRow(name_layout)

       
        self.tab.layout.addRow("创建时间:", QLabel(self.format_time(createTime)))

      
        if isFile:
            self.tab.layout.addRow("修改时间:", QLabel(self.format_time(updateTime)))
        else:
            self.tab.layout.addRow("内部项目:", QLabel(str(child)))

        self.tab.setLayout(self.tab.layout)

       
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def format_time(self, t):
        return f"{t.tm_year}年{t.tm_mon}月{t.tm_mday}日 {t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}"



class ListWidget(QListWidget):
    def __init__(self, curNode, parents, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)  
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  
        self.setDefaultDropAction(Qt.CopyAction)
        self.edited_item = self.currentItem()
        self.close_flag = True
        self.currentItemChanged.connect(self.close_edit)
        self.curNode = curNode
        self.parents = parents
        self.isEdit = False

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        if e.key() == Qt.Key_Return:
            if self.close_flag:
                self.close_edit()
            self.close_flag = True

    def edit_new_item(self) -> None:
        self.close_flag = False
        self.close_edit()
        count = self.count()
        self.addItem('')
        item = self.item(count)
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)

    def item_double_clicked(self, modelindex: QModelIndex) -> None:
       
        return

    def editLast(self, index=-1) -> None:
        self.close_edit()
        item = self.item(self.count() - 1)
        self.setCurrentItem(item)
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)
        self.isEdit = True
        self.index = index

    def editSelected(self, index) -> None:
        self.close_edit()
        item = self.selectedItems()[-1]
        self.setCurrentItem(item)
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)
        self.isEdit = True
        self.index = index

    def close_edit(self, *_) -> None:
        if self.edited_item:
            self.isEdit = False
            self.closePersistentEditor(self.edited_item)
           
            while True:
                sameName = False
                for i in range(len(self.curNode.children) - 1):
                    if self.edited_item.text() == self.curNode.children[i].name and self.index != i:
                        self.edited_item.setText(self.edited_item.text() + "(2)")
                        sameName = True
                        break
                if not sameName:
                    break

           

            self.curNode.children[self.index].name = self.edited_item.text()
            
            self.parents.update_tree()

            self.edited_item = None

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        if e.mimeData().hasText():
            if e.mimeData().text().startswith('file:///'):
                e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e: QDragMoveEvent) -> None:
        e.accept()

    def dropEvent(self, e: QDropEvent) -> None:
        paths = e.mimeData().text().split('\n')
        for path in paths:
            path = path.strip()
            if len(path) > 8:
                self.addItem(path.strip()[8:])
        e.accept()

