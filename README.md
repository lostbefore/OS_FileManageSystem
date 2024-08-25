### 文件管理系统项目说明文档

#### 项目简介

文件管理系统（File Management System）是一个基于 `PyQt5` 实现的图形用户界面（GUI）应用程序。该系统允许用户浏览、管理和操作文件和目录。它使用自定义的文件分配表（FAT）来管理文件存储，模拟了文件系统的基本操作，如创建文件、删除文件、打开文件和显示目录结构等功能。

#### 项目功能

1. **文件浏览**：用户可以通过图形界面浏览文件和目录，查看文件和目录的图标和名称。
2. **文件操作**：支持创建文件、删除文件、打开文件、重命名文件等基本操作。
3. **目录导航**：通过地址栏和导航栏，可以快速定位到特定目录。
4. **进度显示**：显示当前文件系统的使用情况，包括进度条。
5. **上下文菜单**：通过右键菜单，可以对文件和目录进行快捷操作。

#### 对应接口函数及其功能

1. **`__init__()`**
   - 功能：初始化文件管理系统窗口，设置窗口特性、菜单、工具栏、导航栏、文件信息和地址栏。
   - 接口函数：`self.project_init()`, `self.set_window_features()`, `self.set_menu()`, `self.set_toolbar()`, `self.set_navigation_bar()`, `self.set_file_info()`, `self.update_address_bar()`
2. **`project_init()`**
   - 功能：初始化文件分配表（FAT），如果不存在则创建新的 FAT，否则从文件加载 FAT。
   - 接口函数：`pickle.load()`, `pickle.dump()`
3. **`set_window_features()`**
   - 功能：设置窗口的布局和特性。
   - 接口函数：`QGridLayout()`, `self.setLayout()`
4. **`set_menu()`**
   - 功能：初始化菜单栏。
   - 接口函数：暂无具体实现内容
5. **`set_toolbar()`**
   - 功能：初始化工具栏。
   - 接口函数：暂无具体实现内容
6. **`set_navigation_bar()`**
   - 功能：初始化导航栏。
   - 接口函数：暂无具体实现内容
7. **`set_file_info()`**
   - 功能：设置文件信息视图，初始化文件列表视图和进度条，加载当前地址的文件信息。
   - 接口函数：`ListWidget()`, `self.load_cur_address()`, `self.show_menu()`, `QShortcut()`
8. **`apply_styles()`**
   - 功能：设置窗口和控件的样式。
   - 接口函数：`self.setStyleSheet()`
9. **`update_address_bar()`**
   - 功能：更新地址栏内容。
   - 接口函数：暂无具体实现内容
10. **`load_cur_address()`**
    - 功能：加载当前目录下的文件和文件夹信息，并更新到文件列表视图中。
    - 接口函数：`self.listView.clear()`, `QListWidgetItem()`, `self.listView.addItem()`
11. **`open_file(index: QModelIndex)`**
    - 功能：根据传入的索引打开相应的文件。
    - 接口函数：暂无具体实现内容
12. **`show_menu(position)`**
    - 功能：在指定位置显示上下文菜单。
    - 接口函数：暂无具体实现内容
13. **`delete()`**
    - 功能：删除选中的文件。
    - 接口函数：暂无具体实现内容
14. **`closeEvent(event)`**
    - 功能：处理窗口关闭事件，根据用户选择决定是否将当前操作写入磁盘。
    - 接口函数：`QMessageBox()`, `pickle.dump()`

#### 主要类和模块

- **`FileSystem`**：主窗口类，包含文件管理系统的主要功能和界面元素。
- **`FAT`**：文件分配表类，管理文件存储和分配。
- **`ListWidget`**：自定义列表视图类，用于显示文件和目录。

#### 功能实现

总体预览

![](C:\Users\user\Desktop\Works\OS_FileManageSystem\other\1.png)

打开/删除/重命名文件，查看文件属性

![](C:\Users\user\Desktop\Works\OS_FileManageSystem\other\2.png)

![](C:\Users\user\Desktop\Works\OS_FileManageSystem\other\5.png)

通过左侧目录树实现跳转

![](C:\Users\user\Desktop\Works\OS_FileManageSystem\other\3.png)

新建文件/文件夹，更改图标大小

![](C:\Users\user\Desktop\Works\OS_FileManageSystem\other\4.png)

下方显示所占空间

![](C:\Users\user\Desktop\Works\OS_FileManageSystem\other\6.png)

#### 项目评估

##### 功能实现的完善程度

文件管理系统项目实现了许多基本功能，包括文件浏览、文件操作、目录导航、进度显示和上下文菜单等。用户可以通过图形界面浏览文件和目录，查看文件和目录的图标和名称，进行基本的文件操作（如删除文件），并通过地址栏和导航栏快速定位到特定目录。进度条显示了文件系统的使用情况，并通过右键菜单可以进行快捷操作。

虽然项目实现了许多基本功能，但仍有一些功能需要进一步完善。例如，文件的创建和重命名功能尚未实现，文件操作的用户体验和界面的美观度有待提升。

##### 优点

1. **界面直观**：项目采用 `PyQt5` 构建图形用户界面，界面直观易用，用户可以通过简单的点击操作完成文件管理。
2. **功能基本完善**：实现了文件浏览、删除文件、目录导航和进度显示等核心功能，能够满足用户基本的文件管理需求。
3. **自定义文件分配表（FAT）**：通过自定义的文件分配表（FAT）模拟文件系统的基本操作，增强了项目的模拟性和可扩展性。
4. **上下文菜单**：通过右键菜单，用户可以快速对文件和目录进行操作，提升了操作的便利性。
5. **样式定制**：通过 CSS 样式表，可以方便地调整界面的颜色和样式，提升用户体验。

##### 不足

1. **功能不够完善**：文件创建和重命名等功能尚未实现，文件操作的完整性有待提高。
2. **用户体验**：界面的美观度和用户体验需要进一步优化，例如文件图标和名称的显示效果、操作提示等。