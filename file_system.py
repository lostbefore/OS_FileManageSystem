import os
import pickle
import PyQt5
import time
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QListWidgetItem, QProgressBar, QShortcut, QListView, QAbstractItemView, QMessageBox, QDesktopWidget, QGridLayout, QWidget, QAction,QLineEdit, QFormLayout,QTreeWidget,QMenu
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import QSize, Qt, QModelIndex
from ui_elements import ListWidget
from fat import FAT
from ui_elements import Catalog,Block,AttributeInterface,FCB,EditingInterface,ListWidget


class FileSystem(QMainWindow):

    def __init__(self):
        super().__init__()

        
        self.project_init()

        
        self.curNode = self.catalog[0]
        self.rootNode = self.curNode
        self.baseUrl = ['root']
        self.lastLoc = -1 
        self.init_ui()
       
    def init_ui(self):

        def set_window_features():
           
            self.resize(1200, 800)
            self.setWindowTitle('文件资源管理器')
            self.setWindowIcon(QIcon('img/folder.ico'))

            window_geometry = self.frameGeometry()
            center_point = QDesktopWidget().availableGeometry().center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())

            self.grid = QGridLayout()
            self.grid.setSpacing(10)
            self.widGet = QWidget()
            self.widGet.setLayout(self.grid)
            self.setCentralWidget(self.widGet)

        def set_menu():
            menubar = self.menuBar()
            menubar.addAction('格式化', self.format)

        def set_toolbar():
            self.tool_bar = self.addToolBar('工具栏')
            self.back_action = QAction(QIcon('img/back.png'), '&返回', self)
            self.back_action.setShortcut('Backspace')
            self.back_action.triggered.connect(self.backward)
            self.tool_bar.addAction(self.back_action)
            self.back_action.setEnabled(False)
            self.forward_action = QAction(QIcon('img/forward.png'), '&前进', self)
            self.forward_action.triggered.connect(self.forward)
            self.tool_bar.addAction(self.forward_action)
            self.forward_action.setEnabled(False)
            self.tool_bar.addSeparator()
            self.cur_address = QLineEdit()
            self.cur_address.setText(' > root')
            self.cur_address.setReadOnly(True)
            self.cur_address.addAction(QIcon('img/folder.png'), QLineEdit.LeadingPosition)
            self.cur_address.setMinimumHeight(40)
            ptrLayout = QFormLayout()
            ptrLayout.addRow(self.cur_address)
            ptrWidget = QWidget()
            ptrWidget.setLayout(ptrLayout)
            ptrWidget.adjustSize()
            self.tool_bar.addWidget(ptrWidget)
            self.tool_bar.setMovable(False)

        def set_navigation_bar():
           
            self.tree = QTreeWidget()
            self.tree.setHeaderLabels(['快速访问'])
            self.tree.setColumnCount(1)
            self.build_tree()
            self.tree.setCurrentItem(self.rootItem)
            self.treeItem = [self.rootItem]
            self.tree.itemClicked['QTreeWidgetItem*', 'int'].connect(self.click_item)
            self.grid.addWidget(self.tree, 1, 0)

        def set_file_info():
            self.listView = ListWidget(self.curNode, parents=self)
            self.listView.setMinimumWidth(800)
            self.listView.setViewMode(QListView.IconMode)
            self.listView.setIconSize(QSize(72, 72))
            self.listView.setGridSize(QSize(100, 100))
            self.listView.setResizeMode(QListView.Adjust)
            self.listView.setMovement(QListView.Static)
            self.listView.setEditTriggers(QAbstractItemView.AllEditTriggers)
            self.listView.doubleClicked.connect(self.open_file)
            self.load_cur_address()
            self.listView.setContextMenuPolicy(Qt.CustomContextMenu)
            self.listView.customContextMenuRequested.connect(self.show_menu)
            self.grid.addWidget(self.listView, 1, 1)
            self.progress_bar = QProgressBar(self)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
            self.grid.addWidget(self.progress_bar, 2, 0, 1, 2)
            self.progress_bar.setValue(int(self.fat.get_usage_percentage() * 100))

           
            QShortcut(QKeySequence(self.tr("Delete")), self, self.delete)

      
        set_window_features()
        set_menu()
        set_toolbar()
        set_navigation_bar()
        set_file_info()
        self.update_address_bar()

   
    def project_init(self):
       
        if not os.path.exists('fat'):
            self.fat = FAT()
            self.fat.fat = [-2] * blockNum
           
            with open('fat', 'wb') as f:
                f.write(pickle.dumps(self.fat))
        else:
            with open('fat', 'rb') as f:
                self.fat = pickle.load(f)

       
        if not os.path.exists('disk'):
            self.disk = []
            for i in range(blockNum):
                self.disk.append(Block(i))
           
            with open('disk', 'wb') as f:
                f.write(pickle.dumps(self.disk))
        else:
            with open('disk', 'rb') as f:
                self.disk = pickle.load(f)

       
        if not os.path.exists('catalog'):
            self.catalog = []
            self.catalog.append(Catalog("root", False, self.fat, self.disk, time.localtime(time.time())))
          
            with open('catalog', 'wb') as f:
                f.write(pickle.dumps(self.catalog))
        else:
            with open('catalog', 'rb') as f:
                self.catalog = pickle.load(f)

   
    def build_tree(self):
        self.tree.clear()

        
        def buildTreeRecursive(node: Catalog, parent: QTreeWidgetItem):
            child = QTreeWidgetItem(parent)
            child.setText(0, node.name)

            if node.isFile:
                child.setIcon(0, QIcon('img/file.png'))
            else:
                if len(node.children) == 0:
                    child.setIcon(0, QIcon('img/folder.png'))
                else:
                    child.setIcon(0, QIcon('img/folderWithFile.png'))
                for i in node.children:
                    buildTreeRecursive(i, child)

            return child

        self.rootItem = buildTreeRecursive(self.catalog[0], self.tree)
       
        self.tree.addTopLevelItem(self.rootItem)
        self.tree.expandAll()

   
    def format(self):
       
        self.listView.close_edit()

        reply = QMessageBox()
        reply.setWindowIcon(QIcon("img/folder.png"))
        reply.setWindowTitle('提醒')
        reply.setIcon(QMessageBox.Warning)
        reply.setText('确定要格式化磁盘？')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('确定')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('取消')
        reply.exec_()
        reply.show()

        if reply.clickedButton() == buttonN:
            return

       
        self.fat = FAT()
        self.fat.fat = [-2] * blockNum
        with open('fat', 'wb') as f:
            f.write(pickle.dumps(self.fat))

        
        self.disk = []
        for i in range(blockNum):
            self.disk.append(Block(i))
        with open('disk', 'wb') as f:
            f.write(pickle.dumps(self.disk))

        
        self.catalog = []
        self.catalog.append(Catalog("root", False, self.fat, self.disk, time.localtime(time.time())))
        with open('catalog', 'wb') as f:
            f.write(pickle.dumps(self.catalog))

       
        self.hide()
        self.main_window = FileSystem()
        self.main_window.show()

        self.update_tree()

    
    def click_item(self, item, column):
        ways = [item]
       
        temp = item
        while temp.parent() is not None:
            temp = temp.parent()
            ways.append(temp)
        ways.reverse()
       
        while self.backward():
            pass
       
        self.baseUrl = self.baseUrl[:1]
        self.treeItem = self.treeItem[:1]

        
        for i in ways:
            if i == self.rootItem:
                continue
           
            newNode = next((j for j in self.curNode.children if j.name == i.text(0)), None)
            
            if newNode is not None and not newNode.isFile:
                self.curNode = newNode
                
                self.load_cur_address()
                self.listView.curNode = self.curNode
                self.baseUrl.append(newNode.name)

                
                selectedItem = next((self.treeItem[-1].child(j) for j in range(self.treeItem[-1].childCount()) if
                                     self.treeItem[-1].child(j).text(0) == newNode.name), None)
                if selectedItem is not None:
                    self.treeItem.append(selectedItem)
                    self.tree.setCurrentItem(selectedItem)
                else:
                    break

        
        self.update_address_bar()
        
        self.back_action.setEnabled(self.curNode != self.rootNode)
        self.forward_action.setEnabled(False)
        
        self.lastLoc = -1

    
    def open_file(self, modelindex: QModelIndex) -> None:
       
        self.listView.close_edit()

        try:
           
            item = self.listView.item(modelindex.row())
        except:
            
            if len(self.listView.selectedItems()) == 0:
                return
           
            item = self.listView.selectedItems()[-1]

       
        if self.lastLoc != -1 and self.nextStep:
            
            item = self.listView.item(self.lastLoc)
            self.lastLoc = -1
            self.forward_action.setEnabled(False)
        self.nextStep = False

       
        newNode = None
        for i in self.curNode.children:
            if i.name == item.text():
                newNode = i
                break

        
        def getData(parameter):
           
            newNode.data.update(parameter, self.fat, self.disk)
            newNode.updateTime = time.localtime(time.time())

       
        if newNode.isFile:
           
            data = newNode.data.read(self.fat, self.disk)
            self.child = EditingInterface(newNode.name, data)
            self.child._signal.connect(getData)
            self.child.show()
            self.writeFile = newNode
       
        else:
            self.listView.close_edit()

            self.curNode = newNode
            self.load_cur_address()
            self.listView.curNode = self.curNode

            self.baseUrl.append(newNode.name)

            for i in range(self.treeItem[-1].childCount()):
                if self.treeItem[-1].child(i).text(0) == newNode.name:
                    selectedItem = self.treeItem[-1].child(i)
            self.treeItem.append(selectedItem)
            self.tree.setCurrentItem(selectedItem)
            self.back_action.setEnabled(True)

            self.update_address_bar()

        self.update_tree()

    def backward(self):
        self.listView.close_edit()

        if self.rootNode == self.curNode:
            return False

        for i in range(len(self.curNode.parent.children)):
            if self.curNode.parent.children[i].name == self.curNode.name:
                self.lastLoc = i
                self.forward_action.setEnabled(True)
                break

        self.curNode = self.curNode.parent
        self.load_cur_address()
        self.listView.curNode = self.curNode

        self.baseUrl.pop()
        self.treeItem.pop()
        self.tree.setCurrentItem(self.treeItem[-1])
        self.update_tree()
        self.update_address_bar()

        if self.curNode == self.rootNode:
            self.back_action.setEnabled(False)

        return True

    def forward(self):
        self.nextStep = True
        self.open_file(QModelIndex())

    def update_address_bar(self):
        self.statusBar().showMessage(str(len(self.curNode.children)) + '个项目')
        s = '> root'
        for i, item in enumerate(self.baseUrl):
            if i == 0:
                continue
            s += " > " + item
        self.cur_address.setText(s)
        self.update_tree()

    def rename(self):
        if len(self.listView.selectedItems()) == 0:
            return
        self.listView.editSelected(self.listView.selectedIndexes()[-1].row())
        self.update_tree()

    def delete(self):
        if len(self.listView.selectedItems()) == 0:
            return

        item = self.listView.selectedItems()[-1]
        index = self.listView.selectedIndexes()[-1].row()

        reply = QMessageBox()
        reply.setIcon(QMessageBox.Warning)
        reply.setWindowIcon(QIcon("img/folder.ico"))
        reply.setWindowTitle('提醒')
        if self.curNode.children[index].isFile:
            reply.setText('确定要删除文件 "' + item.text() + '" 吗？')
        else:
            reply.setText('确定要删除文件夹 "' + item.text() + '" 及其内部所有内容吗？')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('确定')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('取消')

        reply.exec_()

        if reply.clickedButton() == buttonN:
            return

        self.listView.takeItem(index)
        del item

        def deleteFileRecursive(node):
            if node.isFile:
                node.data.delete(self.fat, self.disk)
            else:
                for i in node.children:
                    deleteFileRecursive(i)

        deleteFileRecursive(self.curNode.children[index])
        self.curNode.children.remove(self.curNode.children[index])

        def updateCatalog(node):
            if node.isFile:
                return [node]
            else:
                x = [node]
                for i in node.children:
                    x += updateCatalog(i)
                return x

        self.catalog = updateCatalog(self.rootNode)
        self.update_tree()

    def create_folder(self):

        self.item_1 = QListWidgetItem(QIcon("img/folder.png"), "新建文件夹")
        self.listView.addItem(self.item_1)
        self.listView.editLast()

        newNode = Catalog(self.item_1.text(), False, self.fat, self.disk, time.localtime(time.time()), self.curNode)
        self.curNode.children.append(newNode)
        self.catalog.append(newNode)

        self.update_tree()

    def create_file(self):
        self.item_1 = QListWidgetItem(QIcon("img/file.png"), "新建文件")
        self.listView.addItem(self.item_1)
        self.listView.editLast()

        newNode = Catalog(self.item_1.text(), True, self.fat, self.disk, time.localtime(time.time()), self.curNode)
        self.curNode.children.append(newNode)
        self.catalog.append(newNode)

        self.update_tree()

    def show_menu(self, point):
        menu = QMenu(self.listView)

        def viewAttribute():
            if len(self.listView.selectedItems()) == 0:
                self.child = AttributeInterface(self.curNode.name, False, self.curNode.createTime,
                                                self.curNode.updateTime,
                                                len(self.curNode.children))

                self.child.show()
                return
            else:
                node = self.curNode.children[self.listView.selectedIndexes()[-1].row()]
                if node.isFile:
                    self.child = AttributeInterface(node.name, node.isFile, node.createTime, node.updateTime, 0)
                else:
                    self.child = AttributeInterface(node.name, node.isFile, node.createTime, node.updateTime,
                                                    len(node.children))
                self.child.show()
                return

        if len(self.listView.selectedItems()) != 0:
            action_open_file = QAction(QIcon('img/open.png'), '打开')
            action_open_file.triggered.connect(self.open_file)
            menu.addAction(action_open_file)

            action_delete_file = QAction(QIcon('img/delete.png'), '删除')
            action_delete_file.triggered.connect(self.delete)
            menu.addAction(action_delete_file)

            action_rename_file = QAction(QIcon('img/rename.png'), '重命名')
            action_rename_file.triggered.connect(self.rename)
            menu.addAction(action_rename_file)

            action_view_attributes = QAction(QIcon('img/attribute.png'), '属性')
            action_view_attributes.triggered.connect(viewAttribute)
            menu.addAction(action_view_attributes)


        else:
            viewMenu = QMenu(menu)
            viewMenu.setTitle('查看')
            viewMenu.setIcon(QIcon('img/view.png'))

            def set_icon_and_grid_size(icon_size, grid_size):
                self.listView.setIconSize(QSize(icon_size, icon_size))
                self.listView.setGridSize(QSize(grid_size, grid_size))

            bigIconAction = QAction(QIcon('img/view_big.png'), '大图标')
            bigIconAction.triggered.connect(lambda: set_icon_and_grid_size(172, 200))
            viewMenu.addAction(bigIconAction)

            middleIconAction = QAction(QIcon('img/view_medium.png'), '中等图标')
            middleIconAction.triggered.connect(lambda: set_icon_and_grid_size(72, 100))
            viewMenu.addAction(middleIconAction)

            smallIconAction = QAction(QIcon('img/view_small.png'), '小图标')
            smallIconAction.triggered.connect(lambda: set_icon_and_grid_size(56, 84))
            viewMenu.addAction(smallIconAction)

            menu.addMenu(viewMenu)

            createMenu = QMenu(menu)
            createMenu.setTitle('新建')
            createMenu.setIcon(QIcon('img/create.png'))

            createFolderAction = QAction(QIcon('img/folder.png'), '文件夹')
            createFolderAction.triggered.connect(self.create_folder)
            createMenu.addAction(createFolderAction)

            createFileAction = QAction(QIcon('img/file.png'), '文件')
            createFileAction.triggered.connect(self.create_file)
            createMenu.addAction(createFileAction)

            menu.addMenu(createMenu)

            action_view_attributes = QAction(QIcon('img/attribute.png'), '属性')
            action_view_attributes.triggered.connect(viewAttribute)
            menu.addAction(action_view_attributes)

        dest_point = self.listView.mapToGlobal(point)
        menu.exec_(dest_point)

    def update_tree(self):
        node = self.rootNode
        item = self.rootItem

        def updateTreeRecursive(node: Catalog, item: QTreeWidgetItem):
            item.setText(0, node.name)
            if node.isFile:
                item.setIcon(0, QIcon('img/file.png'))
            else:
                if len(node.children) == 0:
                    item.setIcon(0, QIcon('img/folder.png'))
                else:
                    item.setIcon(0, QIcon('img/folder.png'))
                if item.childCount() < len(node.children):
                    child = QTreeWidgetItem(item)
                elif item.childCount() > len(node.children):
                    for i in range(item.childCount()):
                        if i == item.childCount() - 1:
                            item.removeChild(item.child(i))
                            break
                        if item.child(i).text(0) != node.children[i].name:
                            item.removeChild(item.child(i))
                            break
                for i in range(len(node.children)):
                    updateTreeRecursive(node.children[i], item.child(i))

        if item.childCount() < len(node.children):
            child = QTreeWidgetItem(item)
        elif item.childCount() > len(node.children):
            for i in range(item.childCount()):
                if i == item.childCount() - 1:
                    item.removeChild(item.child(i))
                    break
                if item.child(i).text(0) != node.children[i].name:
                    item.removeChild(item.child(i))
                    break
        for i in range(len(node.children)):
            updateTreeRecursive(node.children[i], item.child(i))

        updateTreeRecursive(node, item)
        self.progress_bar.setValue(int(self.fat.get_usage_percentage() * 100))

    def load_cur_address(self):
        self.listView.clear()

        for i in self.curNode.children:
            if i.isFile:
                self.item_1 = QListWidgetItem(QIcon("img/file.png"), i.name)
                self.listView.addItem(self.item_1)
            else:
                if len(i.children) == 0:
                    self.item_1 = QListWidgetItem(QIcon("img/folder.png"), i.name)
                else:
                    self.item_1 = QListWidgetItem(QIcon("img/folder.png"), i.name)
                self.listView.addItem(self.item_1)

    def closeEvent(self, event):
        self.listView.close_edit()

        reply = QMessageBox()
        reply.setWindowTitle('提醒')
        reply.setWindowIcon(QIcon("img/folder.png"))
        reply.setIcon(QMessageBox.Warning)
        reply.setText('您是否需要将本次操作写入磁盘？')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.Ignore | QMessageBox.No)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('写入')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('取消')
        buttonI = reply.button(QMessageBox.Ignore)
        buttonI.setText('不写入')

        reply.exec_()

        if reply.clickedButton() == buttonI:
            event.accept()
        elif reply.clickedButton() == buttonY:
            with open('fat', 'wb') as f:
                f.write(pickle.dumps(self.fat))
            with open('disk', 'wb') as f:
                f.write(pickle.dumps(self.disk))
            with open('catalog', 'wb') as f:
                f.write(pickle.dumps(self.catalog))

            event.accept()
        else:
            event.ignore()
