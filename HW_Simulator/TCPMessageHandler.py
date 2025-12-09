import threading
import queue
import time
from TCPClient import TCPClient
import logging


class TCPMessageHandler:
    """
    TCP消息处理器基类，管理TCP连接的消息队列和线程
    """

    def __init__(self, host, port, name="TCPHandler"):
        """
        初始化消息处理器

        Args:
            host: 目标主机
            port: 目标端口
            name: 处理器名称，用于日志标识
        """
        self.host = host
        self.port = port
        self.name = name

        # TCP客户端
        self.tcp_client = None

        # 消息队列
        self.send_queue = queue.Queue()  # 发送队列
        self.recv_queue = queue.Queue()  # 接收队列

        # 线程控制
        self.process_thread = None
        self.worker_thread = None
        self.running = False

        # 配置日志
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(f"{name}_{port}")

    def start(self):
        """启动消息处理器"""
        if self.running:
            self.logger.warning(f"{self.name} 已经启动")
            return False

        try:
            # 创建TCP客户端并连接
            self.tcp_client = TCPClient(self.host, self.port)
            if not self.tcp_client.connect():
                self.logger.error(f"{self.name} 连接失败")
                return False

            self.running = True

            # 启动处理线程
            self.process_thread = threading.Thread(
                target=self._process_thread_func,
                name=f"{self.name}_Process",
                daemon=True
            )
            self.process_thread.start()

            # 启动工作线程
            self.worker_thread = threading.Thread(
                target=self._worker_thread_func,
                name=f"{self.name}_Worker",
                daemon=True
            )
            self.worker_thread.start()

            self.logger.info(f"{self.name} 启动成功")
            return True

        except Exception as e:
            self.logger.error(f"{self.name} 启动失败: {e}")
            return False

    def stop(self):
        """停止消息处理器"""
        if not self.running:
            return

        self.running = False

        # 停止TCP客户端
        if self.tcp_client:
            self.tcp_client.disconnect()
            self.tcp_client = None

        # 清空队列
        while not self.send_queue.empty():
            try:
                self.send_queue.get_nowait()
            except queue.Empty:
                break

        while not self.recv_queue.empty():
            try:
                self.recv_queue.get_nowait()
            except queue.Empty:
                break

        self.logger.info(f"{self.name} 已停止")

    def send_message(self, message):
        """
        发送消息（将消息放入发送队列）

        Args:
            message: 要发送的消息（字符串或字节）
        """
        if not self.running:
            self.logger.warning(f"{self.name} 未运行，无法发送消息")
            return False

        try:
            self.send_queue.put(message)
            self.logger.debug(f"{self.name} 消息已加入发送队列")
            return True
        except Exception as e:
            self.logger.error(f"{self.name} 加入发送队列失败: {e}")
            return False

    def _process_thread_func(self):
        """处理线程函数：负责数据收发"""
        self.logger.info(f"{self.name} 处理线程启动")

        while self.running and self.tcp_client and self.tcp_client.is_connected:
            try:
                # 1. 检查发送队列并发送数据
                send_processed = False
                try:
                    if not self.send_queue.empty():
                        message = self.send_queue.get_nowait()
                        if self.tcp_client.send(message):
                            self.logger.debug(f"{self.name} 发送消息成功")
                        else:
                            self.logger.error(f"{self.name} 发送消息失败")
                        send_processed = True
                except queue.Empty:
                    pass

                # 2. 接收数据（不阻塞）
                data = self.tcp_client.receive(timeout=0.0)  # 不阻塞
                if data is not None:
                    self.recv_queue.put(data)
                    self.logger.debug(f"{self.name} 接收到数据，已加入接收队列")

                # 3. 如果没有活动，短暂休眠
                if not send_processed and data is None:
                    time.sleep(0.001)  # 1ms休眠

            except Exception as e:
                # self.logger.error(f"{self.name} 处理线程异常: {e}")
                if self.running:
                    time.sleep(0.1)

        self.logger.info(f"{self.name} 处理线程退出")

    def _worker_thread_func(self):
        """工作线程函数：处理接收到的数据"""
        self.logger.info(f"{self.name} 工作线程启动")

        while self.running:
            try:
                # 检查接收队列并处理数据
                try:
                    data = self.recv_queue.get(timeout=1.0)
                    self._process_received_data(data)
                except queue.Empty:
                    continue

            except Exception as e:
                self.logger.error(f"{self.name} 工作线程异常: {e}")
                if self.running:
                    time.sleep(0.1)

        self.logger.info(f"{self.name} 工作线程退出")

    def _process_received_data(self, data):
        """
        处理接收到的数据（子类必须重写此方法）

        Args:
            data: 接收到的数据
        """
        # 基类实现，子类应该重写这个方法
        self.logger.info(f"{self.name} 收到数据: {data[:100]}...")

    def is_connected(self):
        """检查是否连接"""
        return self.running and self.tcp_client and self.tcp_client.is_connected

    def __del__(self):
        """析构函数"""
        self.stop()