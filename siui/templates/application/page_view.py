from PyQt5.QtCore import pyqtSignal

from siui.core.globals import SiGlobal
from siui.components.widgets import SiLabel, SiToggleButton
from siui.components.widgets.abstracts import ABCSiNavigationBar
from siui.components.widgets import SiDenseHContainer, SiDenseVContainer, SiStackedContainer


class PageButton(SiToggleButton):
    activated = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置自身样式
        self.setBorderRadius(6)
        self.setStateColor("#00FFFFFF", "#10FFFFFF")

        # 创建高光指示条，用于指示被选中
        self.active_indicator = SiLabel(self)
        self.active_indicator.setFixedStyleSheet("border-radius: 2px")
        self.active_indicator.resize(4, 20)
        self.active_indicator.setOpacity(0)

        # 绑定点击事件到切换状态的方法
        self.clicked.connect(self._on_clicked)

    def reloadStyleSheet(self):
        super().reloadStyleSheet()
        self.active_indicator.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {}, stop:1 {});
            """.format(SiGlobal.siui.colors["THEME_TRANSITION_A"], SiGlobal.siui.colors["THEME_TRANSITION_B"])
        )

    def setActive(self, state):
        """
        设置激活状态
        :param state: 状态
        """
        self.setChecked(state)
        self.active_indicator.setOpacityTo(1 if state is True else 0)
        if state is True:
            self.activated.emit()

    def _on_clicked(self):
        self.setActive(True)

        # 遍历统一父对象下的所有同类子控件，全部设为未激活
        for obj in self.parent().children():
            if isinstance(obj, PageButton) and obj != self:
                obj.setActive(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.active_indicator.move(0, (self.height() - self.active_indicator.height()) // 2)


class PageNavigator(ABCSiNavigationBar):
    """
    页面导航栏
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 清空自己的样式表防止继承
        self.setStyleSheet("")

        # 创建容器用于放置按钮
        self.container = SiDenseVContainer(self)
        self.container.setSpacing(8)
        self.container.setAlignCenter(True)

    def addPageButton(self, svg_data, hint, func_when_active, side="top"):
        """
        添加页面按钮
        :param svg_data: 按钮的 svg 数据
        :param hint: 工具提示
        :param func_when_active: 当被激活时调用的函数
        :param side: 添加在哪一侧
        """
        new_page_button = PageButton(self)
        new_page_button.setStyleSheet("background-color: #20FF0000")
        new_page_button.resize(40, 40)
        new_page_button.setHint(hint)
        new_page_button.attachment().setSvgSize(16, 16)
        new_page_button.attachment().load(svg_data)
        new_page_button.activated.connect(func_when_active)

        self.container.addWidget(new_page_button, side=side)
        self.setMaximumIndex(self.maximumIndex() + 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = event.size()

        self.container.resize(size)


class StackedContainerWithShowUpAnimation(SiStackedContainer):
    def setCurrentIndex(self, index: int):
        super().setCurrentIndex(index)

        self.widgets[index].move(0, 64)
        self.widgets[index].moveTo(0, 0)


class PageView(SiDenseHContainer):
    """
    页面视图，包括左侧的导航栏和右侧的页面
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        # 清空自己的样式表防止继承
        self.setStyleSheet("")

        self.setSpacing(0)
        self.setAdjustWidgetsSize(True)

        # 创建导航栏
        self.page_navigator = PageNavigator(self)
        self.page_navigator.setFixedWidth(16+24+16)

        # 创建堆叠容器
        self.stacked_container = StackedContainerWithShowUpAnimation(self)
        self.stacked_container.setFixedStyleSheet("border-top-left-radius:6px; border-bottom-right-radius:8px")

        # <- 添加到水平布局
        self.addWidget(self.page_navigator)
        self.addWidget(self.stacked_container)

    def _get_page_toggle_method(self, index):
        return lambda: self.stacked_container.setCurrentIndex(index)

    def addPage(self, page, svg_data, hint, side="top"):
        """
        添加页面，这会在导航栏添加一个按钮，并在堆叠容器中添加页面
        :param page: 页面控件
        :param svg_data: 按钮的 svg 数据
        :param hint: 工具提示
        :param side: 按钮添加在哪一侧
        """
        self.stacked_container.addWidget(page)
        self.page_navigator.addPageButton(
            svg_data,
            hint,
            self._get_page_toggle_method(self.stacked_container.widgetsAmount() - 1),
            side
        )

    def reloadStyleSheet(self):
        super().reloadStyleSheet()

        self.stacked_container.setStyleSheet("""background-color: {}; border:1px solid {}
            """.format(SiGlobal.siui.colors["INTERFACE_BG_B"], SiGlobal.siui.colors["INTERFACE_BG_C"]))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = event.size()
        w, h = size.width(), size.height()

        self.page_navigator.resize(56, h)
        self.stacked_container.setGeometry(56, 0, w-56, h)