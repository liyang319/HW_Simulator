"""
HWSimulator.py - 硬件仿真器主界面
按图片样式实现，保持原有代码结构
"""

import tkinter as tk
from tkinter import ttk
import threading
from tkinter import ttk, filedialog, messagebox
from TCPClient import TCPClient
from typing import List, Dict
import time
from SignalConfigInfo import SignalConfigInfo


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

        # 初始化TCPClient列表
        self.tcp_clients: List[TCPClient] = []

        # 创建5个TCPClient实例
        for i in range(3):
            tcp_client = TCPClient(host=f"192.168.3.{196 + i}", port=9001)
            self.tcp_clients.append(tcp_client)

        # 新增：初始化SignalConfigInfo列表
        self.signal_configs: List[SignalConfigInfo] = []

        # 为每个节点创建初始的SignalConfigInfo
        for i in range(3):  # 创建3个信号配置，对应3个节点
            config = SignalConfigInfo(
                node_ip=self.tcp_clients[i].host,  # 使用TCPClient的IP
                signal_id="",  # 初始为空，保存时生成
                signal_value_lower=0.0,
                signal_value_upper=100.0,
                dimension="",
                signal_source="",
                unit="",
                calibration_value=0.0,
                signal_value1=0.0,
                signal_value2=0.0,
                signal_value3=0.0
            )
            self.signal_configs.append(config)

        self.signal_configs[0].signal_id = ""
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

        for i in range(1, 4):
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

            # 从TCPClient获取IP地址
            tcp_client = self.tcp_clients[i - 1]
            ip_var = tk.StringVar(value=tcp_client.host)

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

            # 连接按钮 - 初始状态
            button_text = "连接" if not tcp_client.is_connected else "断开"
            button_bg = '#e0e0e0' if not tcp_client.is_connected else '#d0d0d0'

            connect_btn = tk.Button(host_frame,
                                    text=button_text,
                                    font=("微软雅黑", 12),
                                    bg=button_bg,  # 根据连接状态设置背景色
                                    fg='#333333',
                                    bd=0,
                                    relief='flat',
                                    width=8,
                                    padx=5,
                                    pady=2,
                                    highlightthickness=0,
                                    activebackground='#d0d0d0',
                                    activeforeground='#333333')
            connect_btn.pack(side=tk.LEFT, padx=(0, 10))

            # 状态指示灯
            status_canvas = tk.Canvas(host_frame,
                                      width=20,
                                      height=20,
                                      bg='#f5f5f5',
                                      highlightthickness=0)
            status_canvas.pack(side=tk.LEFT)

            # 根据连接状态设置指示灯颜色
            if tcp_client.is_connected:
                status_canvas.create_oval(2, 2, 18, 18, fill='green', outline='green')
            else:
                status_canvas.create_oval(2, 2, 18, 18, fill='red', outline='red')

            # 存储输入框变量
            self.host_entries.append({
                'label': f"主机{i}",
                'ip_var': ip_var,
                'button': connect_btn,
                'status_canvas': status_canvas,
                'tcp_client': tcp_client
            })

            # 绑定按钮事件
            connect_btn.config(command=lambda idx=i - 1: self.connect_host(idx))

    def connect_host(self, index: int):
        """连接或断开主机"""
        tcp_client = self.tcp_clients[index]
        entry = self.host_entries[index]

        if not tcp_client.is_connected:
            # 连接操作
            ip_address = entry['ip_var'].get()  # 从输入框获取当前IP
            host_label = entry['label']

            # 显示连接中消息
            messagebox.showinfo("连接", f"正在连接 {host_label} ({ip_address})")

            # 更新按钮状态为连接中
            entry['button'].config(text="连接中...", bg='#c0c0c0', state='disabled')
            entry['status_canvas'].delete("all")
            entry['status_canvas'].create_oval(2, 2, 18, 18, fill='yellow', outline='yellow')

            # 启动连接线程
            def connect_thread():
                # 只有在点击连接时才更新TCPClient的host
                tcp_client.host = ip_address
                print(f"主机{index + 1} 使用IP: {ip_address}")

                # 尝试连接
                success = tcp_client.connect()

                # 在UI线程中更新界面
                self.root.after(0, lambda: self.update_host_status(index, success, ip_address))

                if success:
                    # 启动数据接收线程
                    recv_thread = threading.Thread(target=self.data_receive_loop,
                                                   args=(index, tcp_client),
                                                   daemon=True)
                    recv_thread.start()

            # 启动连接线程
            thread = threading.Thread(target=connect_thread, daemon=True)
            thread.start()
        else:
            # 断开操作
            tcp_client.disconnect()
            self.update_host_status(index, False, None)

    def update_host_status(self, index: int, connected: bool, ip_address: str = None):
        """更新主机连接状态"""
        entry = self.host_entries[index]
        tcp_client = self.tcp_clients[index]

        if connected and ip_address:
            # 连接成功
            entry['button'].config(text="断开", bg='#d0d0d0', state='normal')
            entry['status_canvas'].delete("all")
            entry['status_canvas'].create_oval(2, 2, 18, 18, fill='green', outline='green')
            messagebox.showinfo("连接成功", f"{entry['label']} ({ip_address}) 连接成功")
        else:
            # 断开连接
            entry['button'].config(text="连接", bg='#e0e0e0', state='normal')
            entry['status_canvas'].delete("all")
            entry['status_canvas'].create_oval(2, 2, 18, 18, fill='red', outline='red')

    def data_receive_loop(self, index: int, tcp_client: TCPClient):
        """数据接收循环"""
        entry = self.host_entries[index]
        host_name = entry['label']

        while tcp_client.is_connected and tcp_client.socket is not None:
            try:
                # 非阻塞接收数据
                data = tcp_client.receive(timeout=0.1)  # 100ms超时

                if data is not None:
                    # 处理接收到的数据
                    data_str = data.decode('utf-8', errors='ignore')
                    print(f"{host_name} 接收到数据: {data_str}")

                    # 这里可以添加数据处理逻辑
                    # 例如：发送响应、更新界面等

                # 短暂的休眠，避免CPU占用过高
                time.sleep(0.01)

            except Exception as e:
                print(f"{host_name} 数据接收异常: {e}")

                # 检查连接状态
                if not tcp_client.is_connected or tcp_client.socket is None:
                    break

                # 尝试接收一次确认连接是否真的断开
                try:
                    test_data = tcp_client.receive(timeout=0.1)
                    if test_data is None:
                        # 连接可能已断开
                        self.root.after(0, lambda idx=index: self.update_host_status(idx, False))
                        break
                except:
                    # 连接已断开
                    self.root.after(0, lambda idx=index: self.update_host_status(idx, False))
                    break

        print(f"{host_name} 数据接收循环结束")

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
            {"name": "信号ID", "width": 25}  # 修改：ID改为信号ID
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
        self.signal_id_labels = []  # 存储信号ID标签引用

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

                elif col_name == "信号ID":  # 修改：处理信号ID列
                    # 如果有保存过的配置，显示对应的signal_id
                    if node_num - 1 < len(self.signal_configs):
                        signal_id_value = self.signal_configs[node_num - 1].signal_id
                    else:
                        signal_id_value = ""

                    signal_id_label = tk.Label(cell_frame,
                                               text=signal_id_value,
                                               font=("微软雅黑", 11),
                                               bg='white',
                                               fg='#333333',
                                               width=col_width,
                                               anchor='w',
                                               padx=5,
                                               pady=6)
                    signal_id_label.pack(fill=tk.X)

                    # 存储标签引用，用于后续更新
                    self.signal_id_labels.append(signal_id_label)

            # 存储节点配置
            self.node_configs.append(node_config)

        # 第三部分：操作按钮
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(20, 0))  # 上方间距20像素

        # 创建按钮容器右对齐
        buttons_container = tk.Frame(button_frame, bg='white')
        buttons_container.pack(side=tk.RIGHT)

        # 定义按钮列表
        button_names = ["导入", "导出", "保存"]

        for i, btn_text in enumerate(button_names):
            # 创建按钮
            btn = tk.Button(buttons_container,
                            text=btn_text,
                            font=("微软雅黑", 12),
                            bg='#e8e8e8',  # 浅灰色背景
                            fg='#000000',  # 黑色文字
                            bd=1,  # 边框
                            relief='solid',  # 浮雕效果
                            width=8,
                            padx=10,
                            pady=2,
                            highlightthickness=0)

            # 绑定点击事件
            if btn_text == "导入":
                btn.config(command=self.import_config)
            elif btn_text == "导出":
                btn.config(command=self.export_config)
            elif btn_text == "保存":
                btn.config(command=self.save_config)

            # 水平排列，按钮之间留出间距
            btn.pack(side=tk.LEFT, padx=(0, 10) if i < len(button_names) - 1 else 0)

    def import_config(self):
        """导入配置"""
        print("导入配置")
        import tkinter.messagebox as messagebox
        messagebox.showinfo("导入", "导入配置功能")

    def export_config(self):
        """导出配置"""
        print("导出配置")
        import tkinter.messagebox as messagebox
        messagebox.showinfo("导出", "导出配置功能")

    def save_config(self):
        """保存配置 - 生成并更新信号ID，保存到SignalConfigInfo"""
        print("保存配置")

        for i, node_config in enumerate(self.node_configs):
            # 获取当前行的下拉框值
            comboboxes = node_config['comboboxes']

            # 1. 获取机柜编号
            cabinet = comboboxes['机柜'].get()
            cabinet_num = cabinet.replace("机柜", "")
            cabinet_code = cabinet_num.zfill(2)  # 01, 02, 03

            # 2. 获取主站编号
            master = comboboxes['主站'].get()
            master_num = master.replace("主站", "")
            master_code = master_num.zfill(2)  # 01, 02, 03

            # 3. 获取从站编号
            slave = comboboxes['从站'].get()
            slave_num = slave.replace("从站", "")
            slave_code = slave_num.zfill(2)  # 01, 02, 03

            # 4. 获取IO卡件类型
            io_card = comboboxes['IO卡件'].get()  # PO, RTD, TC

            # 5. 获取通道编号
            channel = comboboxes['通道'].get()
            channel_code = channel.zfill(2)  # 01, 02, 03, 04, 05, 06

            # 6. 生成信号ID
            signal_id = f"{cabinet_code}_{master_code}_{slave_code}_{io_card}_{channel_code}"

            # 7. 更新信号ID标签
            if i < len(self.signal_id_labels):
                self.signal_id_labels[i].config(text=signal_id)

            # 8. 获取对应的TCPClient主机IP
            tcp_client = None
            if i < len(self.tcp_clients):
                tcp_client = self.tcp_clients[i]

            # 9. 更新对应的SignalConfigInfo
            if i < len(self.signal_configs):
                config = self.signal_configs[i]
                config.signal_id = signal_id
                if tcp_client:
                    config.node_ip = tcp_client.host

                print(f"节点{i + 1} 信号配置已更新:")
                print(f"  IP: {config.node_ip}")
                print(f"  信号ID: {config.signal_id}")
                print(f"  配置摘要: {config.get_config_summary()}")

        # 10. 同步更新信号管理页面的信号ID
        self.update_signal_management_signal_ids()

        # 11. 同步更新仿真页面的信号ID
        self.update_simulation_signal_ids()

        import tkinter.messagebox as messagebox
        messagebox.showinfo("保存成功", "信号ID已更新，配置已保存")

    def update_signal_management_signal_ids(self):
        """更新信号管理页面的信号ID"""
        if not hasattr(self, 'signal_entries') or not self.signal_entries:
            print("信号管理页面未初始化，跳过更新")
            return

        # 遍历信号管理页面的每一行
        for i, row_entries in enumerate(self.signal_entries):
            if i < len(self.signal_configs):
                # 更新信号ID列（第0列）
                signal_id = self.signal_configs[i].signal_id
                row_entries[0].delete(0, tk.END)  # 清空原有内容
                row_entries[0].insert(0, signal_id)  # 插入新的信号ID
                print(f"信号管理页面 第{i + 1}行 信号ID已更新为: {signal_id}")

    def update_simulation_signal_ids(self):
        """更新仿真页面的信号ID"""
        # 检查仿真页面是否已初始化
        if not hasattr(self, 'sim_content') or not self.sim_content.winfo_exists():
            print("仿真页面未初始化，跳过更新")
            return

        # 仿真页面的表格是动态创建的，需要重建或更新
        # 这里我们重新创建仿真页面的表格
        self.recreate_simulation_table()

    def recreate_simulation_table(self):
        """重新创建仿真页面的表格"""
        if not hasattr(self, 'sim_content') or not self.sim_content.winfo_exists():
            return

        # 清除仿真页面的所有子部件
        for widget in self.sim_content.winfo_children():
            widget.destroy()

        # 重新创建仿真页面内容
        self.create_simulation_content()

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
        """创建信号管理内容区域 - 显示signal_configs数据"""
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
        columns = ["信号ID", "上限", "下限", "量纲", "信号源", "单位", "校准", "信号值1", "信号值2", "信号值3"]
        column_count = len(columns)

        # 从signal_configs获取表格数据
        table_data = []
        for config in self.signal_configs:
            row_data = [
                config.signal_id,  # 信号节点
                str(config.signal_value_upper),  # 上限
                str(config.signal_value_lower),  # 下限
                config.dimension,  # 量纲
                config.signal_source,  # 信号源
                config.unit,  # 单位
                str(config.calibration_value),  # 校准
                str(config.signal_value1),  # 信号值1
                str(config.signal_value2),  # 信号值2
                str(config.signal_value3)  # 信号值3
            ]
            table_data.append(row_data)

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

        # 在表格下面添加操作按钮
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(20, 0))  # 上方间距20像素

        # 创建按钮容器右对齐
        buttons_container = tk.Frame(button_frame, bg='white')
        buttons_container.pack(side=tk.RIGHT)

        # 定义按钮列表
        button_names = ["导入", "导出", "保存"]

        for i, btn_text in enumerate(button_names):
            # 创建按钮
            btn = tk.Button(buttons_container,
                            text=btn_text,
                            font=("微软雅黑", 12),
                            bg='#e8e8e8',  # 浅灰色背景
                            fg='#000000',  # 黑色文字
                            bd=1,  # 边框
                            relief='solid',  # 浮雕效果
                            width=8,
                            padx=10,
                            pady=2,
                            highlightthickness=0)

            # 绑定点击事件
            if btn_text == "导入":
                btn.config(command=self.import_signal_config)
            elif btn_text == "导出":
                btn.config(command=self.export_signal_config)
            elif btn_text == "保存":
                btn.config(command=self.save_signal_config)

            # 水平排列，按钮之间留出间距
            btn.pack(side=tk.LEFT, padx=(0, 10) if i < len(button_names) - 1 else 0)

    def import_signal_config(self):
        """导入信号配置"""
        print("导入信号配置")
        import tkinter.messagebox as messagebox
        messagebox.showinfo("导入信号配置", "导入信号配置功能")

    def export_signal_config(self):
        """导出信号配置"""
        print("导出信号配置")
        import tkinter.messagebox as messagebox
        messagebox.showinfo("导出信号配置", "导出信号配置功能")

    def save_signal_config(self):
        """保存信号配置 - 从界面更新到signal_configs"""
        print("保存信号配置")

        # 验证表格行数与signal_configs数量一致
        if len(self.signal_entries) != len(self.signal_configs):
            import tkinter.messagebox as messagebox
            messagebox.showerror("保存错误",
                                 f"数据不匹配: 表格行数={len(self.signal_entries)}, 配置数量={len(self.signal_configs)}")
            return

        try:
            for row_idx, row_entries in enumerate(self.signal_entries):
                if row_idx >= len(self.signal_configs):
                    continue

                config = self.signal_configs[row_idx]

                # 从Entry控件获取值并更新SignalConfigInfo
                # 第0列: 信号节点 (signal_id) - 只读，不更新
                # 第1列: 上限 (signal_value_upper)
                config.signal_value_upper = float(row_entries[1].get())

                # 第2列: 下限 (signal_value_lower)
                config.signal_value_lower = float(row_entries[2].get())

                # 第3列: 量纲 (dimension)
                config.dimension = row_entries[3].get()

                # 第4列: 信号源 (signal_source)
                config.signal_source = row_entries[4].get()

                # 第5列: 单位 (unit)
                config.unit = row_entries[5].get()

                # 第6列: 校准 (calibration_value)
                config.calibration_value = float(row_entries[6].get())

                # 第7列: 信号值1 (signal_value1)
                config.signal_value1 = float(row_entries[7].get())

                # 第8列: 信号值2 (signal_value2)
                config.signal_value2 = float(row_entries[8].get())

                # 第9列: 信号值3 (signal_value3)
                config.signal_value3 = float(row_entries[9].get())

                print(f"信号配置 {row_idx + 1} 已保存:")
                print(f"  信号ID: {config.signal_id}")
                print(f"  上限: {config.signal_value_upper}")
                print(f"  下限: {config.signal_value_lower}")
                print(f"  量纲: {config.dimension}")
                print(f"  信号源: {config.signal_source}")
                print(f"  单位: {config.unit}")
                print(f"  校准: {config.calibration_value}")
                print(f"  信号值1: {config.signal_value1}")
                print(f"  信号值2: {config.signal_value2}")
                print(f"  信号值3: {config.signal_value3}")

            import tkinter.messagebox as messagebox
            messagebox.showinfo("保存成功", "信号配置已保存")

        except ValueError as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("保存错误", f"数值格式错误: {e}")
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("保存错误", f"保存过程中发生错误: {e}")

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
        """创建仿真标签页 - 根据bbb.jpg图片样式"""
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
        self.sim_content = tk.Frame(self.content_container, bg='white')
        self.content_frames.append(self.sim_content)

        # 创建仿真内容区域
        self.create_simulation_content()

        # 默认隐藏
        self.sim_content.pack_forget()

    def create_simulation_content(self):
        """创建仿真内容区域 - 工作状态和操作列居中对齐"""
        # 创建主容器
        main_frame = tk.Frame(self.sim_content, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 表格标题
        title_label = tk.Label(main_frame,
                               text="仿真监控",
                               font=("微软雅黑", 16, "bold"),
                               bg='white',
                               fg='#000000')
        title_label.pack(anchor='w', pady=(0, 20))

        # 使用grid布局创建4列表格
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(fill=tk.X)

        # 定义4列
        columns = ["信号ID", "当前值", "工作状态", "操作"]

        # 表格数据
        data = [
            ["01_01_01_PO_01", "1.11"],
            ["02_02_02_RTD_02", "2.22"],
            ["03_03_03_PO_03", "3.33"]
        ]

        # 存储启动按钮，用于状态更新
        self.sim_start_buttons = []

        # 创建表头
        for col_idx, header in enumerate(columns):
            cell_frame = tk.Frame(table_frame, bg='white')
            cell_frame.grid(row=0, column=col_idx, sticky='nsew', padx=2, pady=2)

            # 工作状态和操作列表头居中对齐
            if col_idx in [2, 3]:  # 第3列（工作状态）和第4列（操作）
                header_anchor = 'center'
            else:
                header_anchor = 'w'

            header_label = tk.Label(cell_frame,
                                    text=header,
                                    font=("微软雅黑", 12, "bold"),
                                    bg='white',
                                    fg='#000000',
                                    anchor=header_anchor)
            header_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, anchor=header_anchor)

        # 创建数据行
        for row_idx, row_data in enumerate(data):
            # 第1列：信号ID
            col1_frame = tk.Frame(table_frame, bg='white')
            col1_frame.grid(row=row_idx + 1, column=0, sticky='nsew', padx=2, pady=2)

            tk.Label(col1_frame,
                     text=row_data[0],
                     font=("微软雅黑", 12),
                     bg='white',
                     fg='#000000',
                     anchor='w').pack(fill=tk.BOTH, expand=True, padx=5, pady=5, anchor='w')

            # 第2列：当前值
            col2_frame = tk.Frame(table_frame, bg='white')
            col2_frame.grid(row=row_idx + 1, column=1, sticky='nsew', padx=2, pady=2)

            tk.Label(col2_frame,
                     text=row_data[1],
                     font=("微软雅黑", 12),
                     bg='white',
                     fg='#000000',
                     anchor='w').pack(fill=tk.BOTH, expand=True, padx=5, pady=5, anchor='w')

            # 第3列：工作状态（圆形）- 居中对齐
            col3_frame = tk.Frame(table_frame, bg='white')
            col3_frame.grid(row=row_idx + 1, column=2, sticky='nsew', padx=(2, 20), pady=2)

            # 创建圆形 - 初始为红色，居中对齐
            canvas = tk.Canvas(col3_frame,
                               width=20,
                               height=20,
                               bg='white',
                               highlightthickness=0)
            canvas.place(relx=0.5, rely=0.5, anchor='center')
            canvas.create_oval(2, 2, 18, 18, fill='red', outline='red')  # 修改：初始为红色

            # 存储canvas引用，用于后续更新状态
            if row_idx == 0:
                self.status_canvas1 = canvas
            elif row_idx == 1:
                self.status_canvas2 = canvas
            else:
                self.status_canvas3 = canvas

            # 第4列：操作（启动按钮）- 居中对齐
            col4_frame = tk.Frame(table_frame, bg='white')
            col4_frame.grid(row=row_idx + 1, column=3, sticky='nsew', padx=(20, 2), pady=2)

            # 创建启动按钮，绑定click事件
            btn = tk.Button(col4_frame,
                            text="启动",  # 初始文字为"启动"
                            font=("微软雅黑", 12),
                            bg='#e8e8e8',
                            fg='#000000',
                            bd=1,
                            relief='solid',
                            width=8,
                            padx=5,
                            pady=2,
                            command=lambda idx=row_idx: self.start_simulation(idx))  # 修改：只传递行索引
            btn.place(relx=0.5, rely=0.5, anchor='center')

            # 存储按钮引用
            self.sim_start_buttons.append(btn)

        # 配置列权重
        table_frame.columnconfigure(0, weight=1, uniform="col")
        table_frame.columnconfigure(1, weight=1, uniform="col")
        table_frame.columnconfigure(2, weight=1, uniform="col")
        table_frame.columnconfigure(3, weight=1, uniform="col")

    def start_simulation(self, index: int):
        """启动仿真"""
        print(f'启动仿真: 行索引={index}')

        # 检查对应的TCPClient是否已连接
        if index < 0 or index >= len(self.tcp_clients):
            messagebox.showerror("错误", f"无效的主机索引: {index}")
            return

        tcp_client = self.tcp_clients[index]

        if not tcp_client.is_connected or tcp_client.socket is None:
            messagebox.showerror("连接错误", f"主机{index + 1} 未连接，请先在主机管理页面连接")
            return

        # 更新按钮状态
        button = self.sim_start_buttons[index]
        if button.cget("text") == "启动":
            # 准备要发送的JSON数据
            json_data = '{"cmd":"ModuleStart"}'

            # 发送数据
            success = tcp_client.send(json_data)

            if success:
                # 更新界面状态
                button.config(text="停止", bg='#d8d8d8')
                # 更新状态指示灯为绿色
                self.update_simulation_status_light(index, 'green')
                messagebox.showinfo("仿真启动", f"向主机{index + 1} 发送启动命令成功")
            else:
                messagebox.showerror("发送失败", f"向主机{index + 1} 发送启动命令失败")
        else:
            # 发送停止命令
            json_data = '{"cmd":"ModuleStop"}'
            success = tcp_client.send(json_data)

            if success:
                # 更新界面状态
                button.config(text="启动", bg='#e8e8e8')
                # 更新状态指示灯为红色
                self.update_simulation_status_light(index, 'red')
                messagebox.showinfo("仿真停止", f"向主机{index + 1} 发送停止命令成功")
            else:
                messagebox.showerror("发送失败", f"向主机{index + 1} 发送停止命令失败")

    def update_simulation_status_light(self, index: int, color: str):
        """更新仿真状态指示灯颜色"""
        canvas = None
        if index == 0:
            canvas = getattr(self, 'status_canvas1', None)
        elif index == 1:
            canvas = getattr(self, 'status_canvas2', None)
        elif index == 2:
            canvas = getattr(self, 'status_canvas3', None)

        if canvas:
            canvas.delete("all")  # 清除原来的圆形
            canvas.create_oval(2, 2, 18, 18, fill=color, outline=color)

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