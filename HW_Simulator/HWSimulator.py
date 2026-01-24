"""
HWSimulator.py - 硬件仿真器主界面
按图片样式实现，保持原有代码结构
"""

import tkinter as tk
from tkinter import ttk


class HWSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulator")
        # 获取屏幕尺寸并设置窗口大小
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        print(f"{screen_width}x{screen_height}")

        # 设置窗口为屏幕大小，并定位到左上角
        self.root.geometry(f"{screen_width}x{screen_height}")

        # 设置窗口背景为白色
        self.root.configure(bg='white')

        # 创建主容器
        self.main_container = tk.Frame(root, bg='white')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 创建自定义标签控件
        self.tab_container = tk.Frame(self.main_container, bg='white')
        self.tab_container.pack(fill=tk.X, pady=0)

        # 创建内容容器
        self.content_container = tk.Frame(self.main_container, bg='#E6F2FF')
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 创建标签页
        self.create_host_management_tab()
        self.create_config_management_tab()
        self.create_signal_management_tab()
        self.create_simulation_tab()

        # 设置标签页平均分布
        self.setup_tab_layout()

    def setup_tab_layout(self):
        """设置标签页平均分布布局"""
        # 计算平均宽度
        tab_count = len(self.tab_container.winfo_children())

        # 让所有标签按钮平均分布
        for i, tab_btn in enumerate(self.tab_container.winfo_children()):
            tab_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def create_host_management_tab(self):
        """创建主机管理标签页"""
        # 创建标签按钮
        tab_btn = tk.Frame(self.tab_container, bg='white', height=40)

        # 标签文本
        tab_label = tk.Label(tab_btn,
                             text="主机管理",
                             font=("微软雅黑", 10, "bold"),
                             bg='white',
                             fg='#333333',
                             padx=10,
                             pady=10)
        tab_label.place(relx=0.5, rely=0.5, anchor='center')

        # 绑定点击事件
        tab_label.bind('<Button-1>', lambda e: self.show_host_content())
        tab_btn.bind('<Button-1>', lambda e: self.show_host_content())

        # 创建内容区域
        self.host_content = tk.Frame(self.content_container, bg='#E6F2FF')

        # 添加内容文本
        content_label = tk.Label(self.host_content,
                                 text="This is some placeholder text on Tab 1",
                                 font=("Arial", 12),
                                 bg='#E6F2FF',
                                 fg='#666666',
                                 justify='center')
        content_label.place(relx=0.5, rely=0.5, anchor='center')

        # 默认显示主机管理内容
        self.host_content.pack(fill=tk.BOTH, expand=True)

    def create_config_management_tab(self):
        """创建构型管理标签页"""
        # 创建标签按钮
        tab_btn = tk.Frame(self.tab_container, bg='#e0e0e0', height=40)

        # 添加右侧分隔线
        separator = tk.Frame(tab_btn, bg='#cccccc', width=1, height=20)
        separator.place(relx=1.0, rely=0.5, anchor='e', y=0)

        # 标签文本
        tab_label = tk.Label(tab_btn,
                             text="构型管理",
                             font=("微软雅黑", 10, "normal"),
                             bg='#e0e0e0',
                             fg='#333333',
                             padx=10,
                             pady=10)
        tab_label.place(relx=0.5, rely=0.5, anchor='center')

        # 绑定点击事件
        tab_label.bind('<Button-1>', lambda e: self.show_config_content())
        tab_btn.bind('<Button-1>', lambda e: self.show_config_content())

        # 创建内容区域
        self.config_content = tk.Frame(self.content_container, bg='#E6F2FF')

        # 添加内容文本
        content_label = tk.Label(self.config_content,
                                 text="构型管理内容",
                                 font=("Arial", 12),
                                 bg='#E6F2FF',
                                 fg='#666666',
                                 justify='center')
        content_label.place(relx=0.5, rely=0.5, anchor='center')

        # 默认隐藏
        self.config_content.pack_forget()

    def create_signal_management_tab(self):
        """创建信号管理标签页"""
        # 创建标签按钮
        tab_btn = tk.Frame(self.tab_container, bg='#e0e0e0', height=40)

        # 添加右侧分隔线
        separator = tk.Frame(tab_btn, bg='#cccccc', width=1, height=20)
        separator.place(relx=1.0, rely=0.5, anchor='e', y=0)

        # 标签文本
        tab_label = tk.Label(tab_btn,
                             text="信号管理",
                             font=("微软雅黑", 10, "normal"),
                             bg='#e0e0e0',
                             fg='#333333',
                             padx=10,
                             pady=10)
        tab_label.place(relx=0.5, rely=0.5, anchor='center')

        # 绑定点击事件
        tab_label.bind('<Button-1>', lambda e: self.show_signal_content())
        tab_btn.bind('<Button-1>', lambda e: self.show_signal_content())

        # 创建内容区域
        self.signal_content = tk.Frame(self.content_container, bg='#E6F2FF')

        # 添加内容文本
        content_label = tk.Label(self.signal_content,
                                 text="信号管理内容",
                                 font=("Arial", 12),
                                 bg='#E6F2FF',
                                 fg='#666666',
                                 justify='center')
        content_label.place(relx=0.5, rely=0.5, anchor='center')

        # 默认隐藏
        self.signal_content.pack_forget()

    def create_simulation_tab(self):
        """创建仿真标签页"""
        # 创建标签按钮
        tab_btn = tk.Frame(self.tab_container, bg='#e0e0e0', height=40)

        # 标签文本
        tab_label = tk.Label(tab_btn,
                             text="仿真",
                             font=("微软雅黑", 10, "normal"),
                             bg='#e0e0e0',
                             fg='#333333',
                             padx=10,
                             pady=10)
        tab_label.place(relx=0.5, rely=0.5, anchor='center')

        # 绑定点击事件
        tab_label.bind('<Button-1>', lambda e: self.show_sim_content())
        tab_btn.bind('<Button-1>', lambda e: self.show_sim_content())

        # 创建内容区域
        self.sim_content = tk.Frame(self.content_container, bg='#E6F2FF')

        # 添加内容文本
        content_label = tk.Label(self.sim_content,
                                 text="仿真内容",
                                 font=("Arial", 12),
                                 bg='#E6F2FF',
                                 fg='#666666',
                                 justify='center')
        content_label.place(relx=0.5, rely=0.5, anchor='center')

        # 默认隐藏
        self.sim_content.pack_forget()

    def show_host_content(self):
        """显示主机管理内容"""
        self.update_tab_appearance(0)
        self.host_content.pack(fill=tk.BOTH, expand=True)
        self.config_content.pack_forget()
        self.signal_content.pack_forget()
        self.sim_content.pack_forget()

    def show_config_content(self):
        """显示构型管理内容"""
        self.update_tab_appearance(1)
        self.host_content.pack_forget()
        self.config_content.pack(fill=tk.BOTH, expand=True)
        self.signal_content.pack_forget()
        self.sim_content.pack_forget()

    def show_signal_content(self):
        """显示信号管理内容"""
        self.update_tab_appearance(2)
        self.host_content.pack_forget()
        self.config_content.pack_forget()
        self.signal_content.pack(fill=tk.BOTH, expand=True)
        self.sim_content.pack_forget()

    def show_sim_content(self):
        """显示仿真内容"""
        self.update_tab_appearance(3)
        self.host_content.pack_forget()
        self.config_content.pack_forget()
        self.signal_content.pack_forget()
        self.sim_content.pack(fill=tk.BOTH, expand=True)

    def update_tab_appearance(self, active_index):
        """更新标签页外观"""
        tabs = self.tab_container.winfo_children()

        for i, tab_btn in enumerate(tabs):
            if i == active_index:
                # 选中状态：白色背景，加粗字体
                tab_btn.config(bg='white')
                for child in tab_btn.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg='white', font=("微软雅黑", 10, "bold"))
            else:
                # 未选中状态：灰色背景，正常字体
                tab_btn.config(bg='#e0e0e0')
                for child in tab_btn.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg='#e0e0e0', font=("微软雅黑", 10, "normal"))


def main():
    """主函数"""
    root = tk.Tk()
    app = HWSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()