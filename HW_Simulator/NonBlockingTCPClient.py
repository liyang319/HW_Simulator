import socket
import select
import logging
from typing import Optional, Union


class NonBlockingTCPClient:
    """
    非阻塞TCP客户端，支持select多路复用
    """

    def __init__(self, host: str = 'localhost', port: int = 8080,
                 timeout: float = 1.0, buffer_size: int = 4096):
        """
        初始化非阻塞TCP客户端

        Args:
            host: 服务器主机地址
            port: 服务器端口号
            timeout: 连接和操作超时时间（秒）
            buffer_size: 接收数据缓冲区大小
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.buffer_size = buffer_size
        self.socket: Optional[socket.socket] = None
        self.is_connected = False

        # 配置日志
        self.logger = logging.getLogger(f"NonBlockingTCP_{port}")

    def connect(self) -> bool:
        """连接到TCP服务器"""
        try:
            # 创建socket对象
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)

            # 设置为非阻塞模式
            self.socket.setblocking(0)

            # 尝试连接
            self.logger.info(f"正在连接到服务器 {self.host}:{self.port}")

            try:
                self.socket.connect((self.host, self.port))
            except BlockingIOError:
                # 非阻塞模式下connect会立即返回
                pass

            # 使用select等待连接完成
            readable, writable, exceptional = select.select([], [self.socket], [self.socket], self.timeout)

            if not writable:
                self.logger.error(f"连接服务器超时（{self.timeout}秒）")
                self._cleanup()
                return False

            if exceptional:
                self.logger.error("连接过程中发生异常")
                self._cleanup()
                return False

            # 检查连接是否成功
            try:
                # 尝试获取socket错误
                err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if err != 0:
                    self.logger.error(f"连接失败，错误码: {err}")
                    self._cleanup()
                    return False
            except:
                pass

            self.is_connected = True
            self.logger.info("连接服务器成功")
            return True

        except Exception as e:
            self.logger.error(f"连接过程中发生错误: {e}")
            self._cleanup()
            return False

    def send(self, data: Union[str, bytes]) -> bool:
        """
        发送数据到服务器（非阻塞）

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

            # 使用select检查socket是否可写
            readable, writable, exceptional = select.select([], [self.socket], [self.socket], 0.1)

            if not writable:
                self.logger.warning("socket不可写，稍后重试")
                return False

            if exceptional:
                self.logger.error("socket异常")
                self._cleanup()
                return False

            # 发送数据
            sent = self.socket.send(data)
            if sent < len(data):
                self.logger.warning(f"只发送了 {sent}/{len(data)} 字节")

            self.logger.debug(f"成功发送 {sent} 字节数据")
            return True

        except socket.timeout:
            self.logger.error("发送数据超时")
        except BrokenPipeError:
            self.logger.error("连接已断开，无法发送数据")
        except Exception as e:
            self.logger.error(f"发送数据过程中发生错误: {e}")

        self._cleanup()
        return False

    def receive(self, timeout: float = 0.01) -> Optional[bytes]:
        """
        从服务器接收数据（非阻塞）

        Args:
            timeout: 接收超时时间

        Returns:
            Optional[bytes]: 接收到的数据，如果没有数据返回None
        """
        if not self.is_connected or self.socket is None:
            self.logger.error("未连接到服务器，请先调用connect()方法")
            return None

        try:
            # 使用select检查socket是否可读
            readable, writable, exceptional = select.select([self.socket], [], [self.socket], timeout)

            if not readable:
                return None  # 没有数据可读

            if exceptional:
                self.logger.error("socket异常")
                self._cleanup()
                return None

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
        except Exception as e:
            self.logger.error(f"接收数据过程中发生错误: {e}")
            self._cleanup()

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