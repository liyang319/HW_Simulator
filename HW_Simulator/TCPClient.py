import socket
import select
import logging
from typing import Optional, Union


class TCPClient:
    """
    TCP客户端类，支持非阻塞和超时接收
    """

    def __init__(self, host: str = 'localhost', port: int = 8080,
                 connect_timeout: float = 5.0, buffer_size: int = 4096):
        """
        初始化TCP客户端

        Args:
            host: 服务器主机地址
            port: 服务器端口号
            connect_timeout: 连接超时时间（秒）
            buffer_size: 接收数据缓冲区大小
        """
        self.host = host
        self.port = port
        self.connect_timeout = connect_timeout
        self.buffer_size = buffer_size
        self.socket: Optional[socket.socket] = None
        self.is_connected = False

        # 配置日志
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(f"TCP_{port}")

    def connect(self) -> bool:
        """
        连接到TCP服务器

        Returns:
            bool: 连接是否成功
        """
        try:
            # 创建socket对象
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.connect_timeout)

            # 连接到服务器
            self.logger.info(f"正在连接到服务器 {self.host}:{self.port}")
            self.socket.connect((self.host, self.port))

            # 连接成功后，设置为非阻塞模式
            self.socket.setblocking(False)

            self.is_connected = True
            self.logger.info("连接服务器成功")
            return True

        except socket.timeout:
            self.logger.error(f"连接服务器超时（{self.connect_timeout}秒）")
        except ConnectionRefusedError:
            self.logger.error("连接被服务器拒绝，请检查服务器是否运行")
        except socket.gaierror as e:
            self.logger.error(f"地址解析错误: {e}")
        except Exception as e:
            self.logger.error(f"连接过程中发生未知错误: {e}")

        self._cleanup()
        return False

    def send(self, data: Union[str, bytes]) -> bool:
        """
        发送数据到服务器

        Args:
            data: 要发送的数据，可以是字符串或字节

        Returns:
            bool: 发送是否成功
        """
        if not self.is_connected or self.socket is None:
            self.logger.error("未连接到服务器，请先调用connect()方法")
            return False

        try:
            # 将字符串转换为字节
            if isinstance(data, str):
                data = data.encode('utf-8')

            # 使用select等待socket可写
            _, writable, exceptional = select.select([], [self.socket], [self.socket], 5.0)

            if exceptional:
                self.logger.error("socket异常，无法发送数据")
                self._cleanup()
                return False

            if not writable:
                self.logger.error("发送超时，socket不可写")
                return False

            # 发送数据
            self.socket.sendall(data)
            self.logger.debug(f"成功发送 {len(data)} 字节数据")
            return True

        except socket.timeout:
            self.logger.error("发送数据超时")
        except BrokenPipeError:
            self.logger.error("连接已断开，无法发送数据")
        except OSError as e:
            self.logger.error(f"发送数据过程中发生错误: {e}")
        except Exception as e:
            self.logger.error(f"发送数据过程中发生未知错误: {e}")

        self._cleanup()
        return False

    def receive(self, timeout: float = 0.0) -> Optional[bytes]:
        """
        从服务器接收数据

        Args:
            timeout: 接收超时时间，0表示不阻塞立即返回，None表示阻塞直到有数据

        Returns:
            Optional[bytes]: 接收到的数据，如果没有数据返回None
        """
        if not self.is_connected or self.socket is None:
            self.logger.error("未连接到服务器，请先调用connect()方法")
            return None

        try:
            # 使用select检查socket是否可读
            readable, _, exceptional = select.select([self.socket], [], [self.socket], timeout)

            if exceptional:
                self.logger.error("socket异常")
                self._cleanup()
                return None

            if not readable:
                return None  # 没有数据可读

            # 接收数据
            data = self.socket.recv(self.buffer_size)
            if not data:
                self.logger.info("连接已关闭")
                self._cleanup()
                return None

            self.logger.debug(f"成功接收 {len(data)} 字节数据")
            return data

        except socket.timeout:
            return None
        except ConnectionResetError:
            self.logger.error("连接被服务器重置")
            self._cleanup()
        except OSError as e:
            self.logger.error(f"接收数据过程中发生错误: {e}")
            self._cleanup()
        except Exception as e:
            self.logger.error(f"接收数据过程中发生未知错误: {e}")
            self._cleanup()

        return None

    def receive_with_timeout(self, timeout: float = 5.0) -> Optional[bytes]:
        """
        带超时接收数据

        Args:
            timeout: 接收超时时间（秒）

        Returns:
            Optional[bytes]: 接收到的数据，如果超时返回None
        """
        return self.receive(timeout)

    def send_and_receive(self, data: Union[str, bytes], timeout: float = 5.0) -> Optional[bytes]:
        """
        发送数据并等待响应

        Args:
            data: 要发送的数据
            timeout: 接收超时时间

        Returns:
            Optional[bytes]: 服务器响应数据
        """
        if self.send(data):
            return self.receive_with_timeout(timeout)
        return None

    def _cleanup(self):
        """清理资源"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.is_connected = False

    def disconnect(self):
        """断开连接"""
        self.logger.info("断开与服务器的连接")
        self._cleanup()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动断开连接"""
        self.disconnect()
