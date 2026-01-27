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
        # screen_width = 1000
        # screen_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
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

        # 创建内容容器 - 添加灰色矩形背景
        self.content_container = tk.Frame(self.main_container, bg='#f5f5f5', bd=2, relief='solid')
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 存储标签容器
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
            # 如果不是第一个标签，先添加一个分隔空白
            if i > 0:
                # 添加左侧分隔空白，使用浅灰色背景
                left_spacer = tk.Frame(self.tab_container, bg='#f5f5f5', width=20)
                left_spacer.pack(side=tk.LEFT, fill=tk.Y)
            tab_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

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

        # 创建主机管理内容区域
        self.host_content = tk.Frame(self.content_container, bg='#f5f5f5')
        self.content_frames.append(self.host_content)

        # 添加主机配置界面
        self.create_host_management_content()

        # 默认显示主机管理内容
        self.host_content.pack(fill=tk.BOTH, expand=True)

    def create_host_management_content(self):
        """创建主机管理内容区域"""
        # 创建主容器 - 背景改为白色
        main_frame = tk.Frame(self.host_content, bg='#f5f5f5')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 标题
        title_label = tk.Label(main_frame,
                               text="主机配置",
                               font=("微软雅黑", 16, "bold"),
                               bg='#f5f5f5',
                               fg='#333333')
        title_label.pack(anchor='w', pady=(0, 20))

        # 创建主机配置表单
        form_frame = tk.Frame(main_frame, bg='#f5f5f5')
        form_frame.pack(fill=tk.BOTH, expand=True)

        # 创建5个主机配置项
        self.host_entries = []

        for i in range(1, 6):
            host_frame = tk.Frame(form_frame, bg='#f5f5f5')
            host_frame.pack(fill=tk.X, pady=5)

            # 主机标签
            host_label = tk.Label(host_frame,
                                  text=f"主机{i}",
                                  font=("微软雅黑", 12),
                                  bg='#f5f5f5',
                                  fg='#333333',
                                  width=8,
                                  anchor='w')
            host_label.pack(side=tk.LEFT, padx=(0, 20))

            # IP地址输入框 - 使用ttk.Combobox实现下拉箭头
            ip_var = tk.StringVar(value=f"192.168.1.{100 + i - 1}")

            # 创建编辑框框架，用于添加边框
            ip_frame = tk.Frame(host_frame, bg='white', bd=1, relief='solid')
            ip_frame.pack(side=tk.LEFT, padx=(0, 20))

            # 创建编辑框
            ip_entry = tk.Entry(ip_frame,
                                textvariable=ip_var,
                                font=("微软雅黑", 12),
                                width=15,
                                bd=0,
                                relief='flat',
                                highlightthickness=0)
            ip_entry.pack(padx=5, pady=5)

            # 连接按钮 - 纯灰色，无边框
            connect_btn = tk.Button(host_frame,
                                    text="连接",
                                    font=("微软雅黑", 12),
                                    bg='#e0e0e0',  # 浅灰色背景
                                    fg='#333333',  # 黑色文字
                                    bd=0,  # 无边框
                                    relief='flat',  # 无浮雕
                                    width=8,
                                    padx=5,
                                    pady=2,
                                    highlightthickness=0,  # 移除高亮边框
                                    activebackground='#d0d0d0',  # 点击时略深的灰色
                                    activeforeground='#333333')
            connect_btn.pack(side=tk.LEFT, padx=(0, 10))

            # 状态指示灯
            status_canvas = tk.Canvas(host_frame,
                                      width=20,
                                      height=20,
                                      bg='#f5f5f5',
                                      highlightthickness=0)
            status_canvas.pack(side=tk.LEFT)

            # 绘制红色圆点
            status_canvas.create_oval(2, 2, 18, 18, fill='red', outline='red')

            # 存储输入框变量
            self.host_entries.append({
                'label': f"主机{i}",
                'ip_var': ip_var,
                'button': connect_btn,
                'status': status_canvas
            })

            # 绑定按钮事件
            connect_btn.config(command=lambda idx=i - 1: self.connect_host(idx))

    def create_config_management_tab(self):
        """创建构型管理标签页 - 根据图片123.jpg样式"""
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
        self.config_content = tk.Frame(self.content_container, bg='white')
        self.content_frames.append(self.config_content)

        # 创建构型管理内容区域
        self.create_config_management_content()

        # 默认隐藏
        self.config_content.pack_forget()

    def create_config_management_content(self):
        """创建构型管理内容区域 - 根据图片样式"""
        # 创建主容器
        main_frame = tk.Frame(self.config_content, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 第一部分：平台对接设置
        platform_frame = tk.Frame(main_frame, bg='white')
        platform_frame.pack(fill=tk.X, pady=(0, 20))

        # 平台对接设置标题
        platform_title = tk.Label(platform_frame,
                                  text="平台对接设置",
                                  font=("微软雅黑", 16, "bold"),
                                  bg='white',
                                  fg='#333333')
        platform_title.pack(anchor='w', pady=(0, 10))

        # 平台选项容器
        options_frame = tk.Frame(platform_frame, bg='white')
        options_frame.pack(anchor='w')

        # 创建平台选项
        platform_options = [
            ("仿真平台", 1),
            ("控制系统", 2),
            ("IO系统", 3),
            ("其他", 4)
        ]

        self.platform_vars = []
        for i, (text, val) in enumerate(platform_options):
            var = tk.IntVar(value=1)  # 默认选中
            self.platform_vars.append(var)

            # 使用Label+Checkbutton组合
            option_frame = tk.Frame(options_frame, bg='white')
            option_frame.pack(side=tk.LEFT, padx=(0, 20))

            # 创建Checkbutton
            check = tk.Checkbutton(option_frame,
                                   text=text,
                                   font=("微软雅黑", 12),
                                   bg='white',
                                   fg='#333333',
                                   variable=var,
                                   onvalue=1,
                                   offvalue=0)
            check.pack(side=tk.LEFT)

            # 存储变量
            self.platform_vars.append(var)

        # 第二部分：控制节点设置
        nodes_frame = tk.Frame(main_frame, bg='white')
        nodes_frame.pack(fill=tk.BOTH, expand=True)

        # 控制节点设置标题
        nodes_title = tk.Label(nodes_frame,
                               text="控制节点设置",
                               font=("微软雅黑", 16, "bold"),
                               bg='white',
                               fg='#333333')
        nodes_title.pack(anchor='w', pady=(0, 10))

        # 创建节点配置容器
        config_container = tk.Frame(nodes_frame, bg='white')
        config_container.pack(fill=tk.BOTH, expand=True)

        # 定义列配置：列名、宽度（字符数）
        column_configs = [
            {"name": "节点", "width": 6},
            {"name": "机柜", "width": 8},
            {"name": "主站", "width": 8},
            {"name": "从站", "width": 8},
            {"name": "IO卡件", "width": 10},
            {"name": "通道", "width": 8},
            {"name": "ID", "width": 25}
        ]

        # 创建列标题
        columns_frame = tk.Frame(config_container, bg='white')
        columns_frame.pack(fill=tk.X, pady=(0, 5))

        for config in column_configs:
            col_name = config["name"]
            col_width = config["width"]

            # 创建标题标签，指定宽度
            title_label = tk.Label(columns_frame,
                                   text=col_name,
                                   font=("微软雅黑", 12, "bold"),
                                   bg='white',
                                   fg='#333333',
                                   width=col_width,
                                   anchor='w',
                                   padx=5,
                                   pady=5)
            title_label.pack(side=tk.LEFT, padx=1)

        # 创建3个节点的配置行
        self.node_configs = []  # 存储节点配置

        for node_num in range(1, 4):  # 创建3个节点
            node_frame = tk.Frame(config_container, bg='white')
            node_frame.pack(fill=tk.X, pady=2)

            # 存储当前节点的配置
            node_config = {
                'node': node_num,
                'comboboxes': {}
            }

            for col_idx, config in enumerate(column_configs):
                col_name = config["name"]
                col_width = config["width"]

                cell_frame = tk.Frame(node_frame, bg='white')
                cell_frame.pack(side=tk.LEFT, padx=1)

                if col_name == "节点":  # 节点号
                    node_label = tk.Label(cell_frame,
                                          text=str(node_num),
                                          font=("微软雅黑", 11),
                                          bg='white',
                                          fg='#333333',
                                          width=col_width,
                                          anchor='w',
                                          padx=5,
                                          pady=6)
                    node_label.pack(fill=tk.X)

                elif col_name in ["机柜", "主站", "从站", "IO卡件", "通道"]:  # 使用下拉框
                    # 根据列确定下拉框的选项
                    if col_name == "机柜":
                        values = ["机柜1", "机柜2", "机柜3"]
                        default = f"机柜{node_num}"
                    elif col_name == "主站":
                        values = ["主站1", "主站2", "主站3"]
                        default = f"主站{node_num}"
                    elif col_name == "从站":
                        values = ["从站1", "从站2", "从站3"]
                        default = f"从站{node_num}"
                    elif col_name == "IO卡件":
                        values = ["PO", "RTD", "TC"]
                        default = ["PO", "RTD", "TC"][node_num - 1]  # PO, RTD, TC
                    elif col_name == "通道":
                        values = ["1", "2", "3", "4", "5", "6"]
                        default = str(node_num)

                    # 创建下拉框，指定宽度
                    combobox = ttk.Combobox(cell_frame,
                                            values=values,
                                            font=("微软雅黑", 11),
                                            width=col_width,
                                            state="readonly")
                    combobox.set(default)
                    combobox.pack(fill=tk.X, padx=5, pady=3)

                    # 存储下拉框引用
                    node_config['comboboxes'][col_name] = combobox

                elif col_name == "ID":  # ID
                    # 生成ID值
                    id_mapping = {
                        1: "01_01_01_PO_01",
                        2: "02_02_02_RTD_02",
                        3: "03_03_03_PO_03"
                    }
                    id_value = id_mapping.get(node_num, "")

                    id_label = tk.Label(cell_frame,
                                        text=id_value,
                                        font=("微软雅黑", 11),
                                        bg='white',
                                        fg='#333333',
                                        width=col_width,
                                        anchor='w',
                                        padx=5,
                                        pady=6)
                    id_label.pack(fill=tk.X)

            # 存储节点配置
            self.node_configs.append(node_config)

    def show_config_content(self):
        """显示构型管理内容"""
        print('显示构型管理')
        self.update_tab_appearance(1)
        # 隐藏所有内容区域
        for content_frame in self.content_frames:
            content_frame.pack_forget()
        # 显示选中内容区域
        self.config_content.pack(fill=tk.BOTH, expand=True)
        # 强制更新界面布局
        self.config_content.update_idletasks()

    def create_signal_management_tab(self):
        """创建信号管理标签页 - 根据图片样式"""
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
        self.signal_content = tk.Frame(self.content_container, bg='white')
        self.content_frames.append(self.signal_content)

        # 创建信号管理内容区域
        self.create_signal_management_content()

        # 默认隐藏
        self.signal_content.pack_forget()

    def create_signal_management_content(self):
        """创建信号管理内容区域 - 简单铺满版本"""
        # 创建主容器
        main_frame = tk.Frame(self.signal_content, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 表格标题
        title_label = tk.Label(main_frame,
                               text="信号管理",
                               font=("微软雅黑", 16, "bold"),
                               bg='white',
                               fg='#000000')
        title_label.pack(anchor='w', pady=(0, 20))

        # 创建表格容器
        table_container = tk.Frame(main_frame, bg='white', bd=0, relief='solid')
        table_container.pack(fill=tk.BOTH, expand=True)

        # 创建内部表格框架
        inner_frame = tk.Frame(table_container, bg='white')
        inner_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # 填满容器

        # 表格列配置
        columns = ["信号节点", "上限", "下限", "量纲", "信号源", "单位", "校准", "信号值1", "信号值2", "信号值3"]
        column_count = len(columns)

        # 表格数据
        table_data = [
            ["01_01_01_PO_01", "", "", "", "", "", "", "", "", ""],
            ["02_02_02_RTD_02", "", "", "", "", "", "", "", "", ""],
            ["03_03_03_PO_03", "", "", "", "", "", "", "", "", ""]
        ]

        # 存储所有Entry控件
        self.signal_entries = []

        # 创建表头
        for col_idx, col_name in enumerate(columns):
            # 计算相对位置
            rel_x = col_idx / column_count
            rel_width = 1 / column_count

            # 创建表头单元格
            header_cell = tk.Frame(inner_frame, bg='#f0f0f0')
            header_cell.place(relx=rel_x, y=0, relwidth=rel_width, height=40)

            # 添加边框
            # 上边框
            border_top = tk.Frame(header_cell, bg='#000000', height=1)
            border_top.place(x=0, y=0, relwidth=1, height=1)

            # 右边框
            border_right = tk.Frame(header_cell, bg='#000000', width=1)
            border_right.place(relx=1.0, y=0, x=-1, width=1, relheight=1)

            # 下边框
            border_bottom = tk.Frame(header_cell, bg='#000000', height=1)
            border_bottom.place(x=0, y=39, relwidth=1, height=1)

            # 左边框 - 为第一个单元格添加左边框
            if col_idx == 0:
                border_left = tk.Frame(header_cell, bg='#000000', width=1)
                border_left.place(x=0, y=0, width=1, relheight=1)

            # 表头标签
            header_label = tk.Label(header_cell,
                                    text=col_name,
                                    font=("微软雅黑", 12, "bold"),
                                    bg='#f0f0f0',
                                    fg='#000000',
                                    anchor='center')
            header_label.place(relx=0.5, rely=0.5, anchor='center')

        # 创建数据行
        for row_idx, row_data in enumerate(table_data):
            row_entries = []
            for col_idx, cell_value in enumerate(row_data):
                # 计算相对位置
                rel_x = col_idx / column_count
                rel_width = 1 / column_count
                y_pos = 40 + row_idx * 40

                # 创建单元格框架
                cell_frame = tk.Frame(inner_frame, bg='white')
                cell_frame.place(relx=rel_x, y=y_pos, relwidth=rel_width, height=40)

                # 添加边框
                border_left = tk.Frame(cell_frame, bg='#000000', width=1)
                border_left.place(x=0, y=0, width=1, relheight=1)

                border_bottom = tk.Frame(cell_frame, bg='#000000', height=1)
                border_bottom.place(x=0, y=39, relwidth=1, height=1)

                if col_idx == column_count - 1:  # 最后一列添加右边框
                    border_right = tk.Frame(cell_frame, bg='#000000', width=1)
                    border_right.place(relx=1.0, y=0, x=-1, width=1, relheight=1)

                # 创建Entry控件
                cell_entry = tk.Entry(cell_frame,
                                      font=("微软雅黑", 11),
                                      bd=0,
                                      highlightthickness=0,
                                      bg='white',
                                      fg='#000000',
                                      justify='center')
                cell_entry.insert(0, cell_value)
                cell_entry.place(relx=0.5, rely=0.5, anchor='center',
                                 relwidth=0.9, relheight=0.7)  # 使用相对宽度

                row_entries.append(cell_entry)

            self.signal_entries.append(row_entries)

    def show_signal_content(self):
        """显示信号管理内容"""
        print('显示信号管理')
        self.update_tab_appearance(2)
        # 隐藏所有内容区域
        for content_frame in self.content_frames:
            content_frame.pack_forget()
        # 显示选中内容区域
        self.signal_content.pack(fill=tk.BOTH, expand=True)
        # 强制更新界面布局
        self.signal_content.update_idletasks()

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
        print('显示主站管理')
        self.update_tab_appearance(0)
        # 隐藏所有内容区域
        for content_frame in self.content_frames:
            content_frame.pack_forget()
        # 显示选中内容区域
        self.host_content.pack(fill=tk.BOTH, expand=True)
        # 强制更新界面布局
        self.host_content.update_idletasks()


    def show_sim_content(self):
        """显示仿真内容"""
        print('显示仿真')
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