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
        # screen_width = self.root.winfo_screenwidth()
        # screen_height = self.root.winfo_screenheight()
        screen_width = 1000
        screen_height = 800
        print(f"{screen_width}x{screen_height}")

        # 设置窗口为屏幕大小，并定位到左上角
        self.root.geometry(f"{screen_width}x{screen_height}")

        # 设置窗口背景为统一的浅灰色
        self.root.configure(bg='#f5f5f5')

        # 创建主容器
        self.main_container = tk.Frame(root, bg='#f5f5f5')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 创建自定义标签控件
        self.tab_container = tk.Frame(self.main_container, bg='white')
        self.tab_container.pack(fill=tk.X, pady=(20, 0), padx=20)

        # 创建内容容器 - 统一背景色
        self.content_container = tk.Frame(self.main_container, bg='#f5f5f5')
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 存储所有标签容器
        self.tab_labels = []
        self.tab_frames = []
        # 存储所有内容区域
        self.content_frames = []

        # 创建标签页
        self.create_host_management_tab()
        self.create_config_management_tab()
        self.create_signal_management_tab()
        self.create_simulation_tab()

        # 设置标签页平均分布
        self.setup_tab_layout()

    def setup_tab_layout(self):
        """设置标签页平均分布布局"""
        # 让所有标签按钮平均分布
        for i, tab_btn in enumerate(self.tab_frames):
            tab_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)

    def create_host_management_tab(self):
        """创建主站管理标签页"""
        # 创建标签按钮容器
        tab_btn = tk.Frame(self.tab_container, bg='white', height=40)
        self.tab_frames.append(tab_btn)

        # 标签文本
        self.host_label = tk.Label(tab_btn,
                                   text="主站管理",
                                   font=("微软雅黑", 10, "bold"),
                                   bg='white',
                                   fg='#333333',
                                   padx=20,
                                   pady=10)
        self.host_label.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.tab_labels.append(self.host_label)

        # 绑定点击事件
        self.host_label.bind('<Button-1>', lambda e: self.show_host_content())
        tab_btn.bind('<Button-1>', lambda e: self.show_host_content())

        # 创建内容区域
        self.host_content = tk.Frame(self.content_container, bg='#f5f5f5')
        self.content_frames.append(self.host_content)

        # 添加内容文本
        self.host_content_label = tk.Label(self.host_content,
                                           text="主站管理内容区域",
                                           font=("Arial", 12),
                                           bg='#f5f5f5',
                                           fg='#333333',
                                           justify='center')
        self.host_content_label.place(relx=0.5, rely=0.5, anchor='center')

        # 默认显示主机管理内容
        self.host_content.pack(fill=tk.BOTH, expand=True)

    def create_config_management_tab(self):
        """创建构型管理标签页"""
        # 创建标签按钮容器
        tab_btn = tk.Frame(self.tab_container, bg='white', height=40)
        self.tab_frames.append(tab_btn)

        # 标签文本
        self.config_label = tk.Label(tab_btn,
                                     text="构型管理",
                                     font=("微软雅黑", 10, "normal"),
                                     bg='#e0e0e0',
                                     fg='#333333',
                                     padx=20,
                                     pady=10)
        self.config_label.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.tab_labels.append(self.config_label)

        # 绑定点击事件
        self.config_label.bind('<Button-1>', lambda e: self.show_config_content())
        tab_btn.bind('<Button-1>', lambda e: self.show_config_content())

        # 创建内容区域
        self.config_content = tk.Frame(self.content_container, bg='#f5f5f5')
        self.content_frames.append(self.config_content)

        # 添加内容文本
        self.config_content_label = tk.Label(self.config_content,
                                             text="构型管理内容区域",
                                             font=("Arial", 12),
                                             bg='#f5f5f5',
                                             fg='#333333',
                                             justify='center')
        self.config_content_label.place(relx=0.5, rely=0.5, anchor='center')

        # 默认隐藏
        self.config_content.pack_forget()

    def create_signal_management_tab(self):
        """创建信号管理标签页"""
        # 创建标签按钮容器
        tab_btn = tk.Frame(self.tab_container, bg='white', height=40)
        self.tab_frames.append(tab_btn)

        # 标签文本
        self.signal_label = tk.Label(tab_btn,
                                     text="信号管理",
                                     font=("微软雅黑", 10, "normal"),
                                     bg='#e0e0e0',
                                     fg='#333333',
                                     padx=20,
                                     pady=10)
        self.signal_label.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.tab_labels.append(self.signal_label)

        # 绑定点击事件
        self.signal_label.bind('<Button-1>', lambda e: self.show_signal_content())
        tab_btn.bind('<Button-1>', lambda e: self.show_signal_content())

        # 创建内容区域
        self.signal_content = tk.Frame(self.content_container, bg='#f5f5f5')
        self.content_frames.append(self.signal_content)

        # 添加内容文本
        self.signal_content_label = tk.Label(self.signal_content,
                                             text="信号管理内容区域",
                                             font=("Arial", 12),
                                             bg='#f5f5f5',
                                             fg='#333333',
                                             justify='center')
        self.signal_content_label.place(relx=0.5, rely=0.5, anchor='center')

        # 默认隐藏
        self.signal_content.pack_forget()

    def create_simulation_tab(self):
        """创建仿真标签页"""
        # 创建标签按钮容器
        tab_btn = tk.Frame(self.tab_container, bg='white', height=40)
        self.tab_frames.append(tab_btn)

        # 标签文本
        self.sim_label = tk.Label(tab_btn,
                                  text="仿真",
                                  font=("微软雅黑", 10, "normal"),
                                  bg='#e0e0e0',
                                  fg='#333333',
                                  padx=20,
                                  pady=10)
        self.sim_label.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.tab_labels.append(self.sim_label)

        # 绑定点击事件
        self.sim_label.bind('<Button-1>', lambda e: self.show_sim_content())
        tab_btn.bind('<Button-1>', lambda e: self.show_sim_content())

        # 创建内容区域
        self.sim_content = tk.Frame(self.content_container, bg='#f5f5f5')
        self.content_frames.append(self.sim_content)

        # 添加内容文本
        self.sim_content_label = tk.Label(self.sim_content,
                                          text="仿真内容区域",
                                          font=("Arial", 12),
                                          bg='#f5f5f5',
                                          fg='#333333',
                                          justify='center')
        self.sim_content_label.place(relx=0.5, rely=0.5, anchor='center')

        # 默认隐藏
        self.sim_content.pack_forget()

    def show_host_content(self):
        """显示主站管理内容"""
        print('show_host_content')
        self.update_tab_appearance(0)
        # 隐藏所有内容区域
        for content_frame in self.content_frames:
            content_frame.pack_forget()
        # 显示选中内容区域
        self.host_content.pack(fill=tk.BOTH, expand=True)
        # 强制更新界面布局
        self.host_content.update_idletasks()

    def show_config_content(self):
        """显示构型管理内容"""
        print('show_config_content')
        self.update_tab_appearance(1)
        # 隐藏所有内容区域
        for content_frame in self.content_frames:
            content_frame.pack_forget()
        # 显示选中内容区域
        self.config_content.pack(fill=tk.BOTH, expand=True)
        # 强制更新界面布局
        self.config_content.update_idletasks()

    def show_signal_content(self):
        """显示信号管理内容"""
        print('show_signal_content')
        self.update_tab_appearance(2)
        # 隐藏所有内容区域
        for content_frame in self.content_frames:
            content_frame.pack_forget()
        # 显示选中内容区域
        self.signal_content.pack(fill=tk.BOTH, expand=True)
        # 强制更新界面布局
        self.signal_content.update_idletasks()

    def show_sim_content(self):
        """显示仿真内容"""
        print('show_sim_content')
        self.update_tab_appearance(3)
        # 隐藏所有内容区域
        for content_frame in self.content_frames:
            content_frame.pack_forget()
        # 显示选中内容区域
        self.sim_content.pack(fill=tk.BOTH, expand=True)
        # 强制更新界面布局
        self.sim_content.update_idletasks()

    def update_tab_appearance(self, active_index):
        """更新标签页外观"""
        tab_texts = ["主站管理", "构型管理", "信号管理", "仿真"]

        for i, label in enumerate(self.tab_labels):
            if i == active_index:
                # 选中状态：白色背景，加粗字体
                label.config(
                    bg='white',
                    font=("微软雅黑", 10, "bold"),
                    text=tab_texts[i]
                )
            else:
                # 未选中状态：灰色背景，正常字体
                label.config(
                    bg='#e0e0e0',
                    font=("微软雅黑", 10, "normal"),
                    text=tab_texts[i]
                )


def main():
    """主函数"""
    root = tk.Tk()
    app = HWSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()