try:
    from socket import inet_pton
except ImportError:
    from typing import TYPE_CHECKING
    if not TYPE_CHECKING:
        # based on https://gist.github.com/nnemkin/4966028
        # this code only applies on Windows Python 2.7
        import ctypes
        import socket

        class SockAddr(ctypes.Structure):
            _fields_ = [
                ("sa_family", ctypes.c_short),
                ("__pad1", ctypes.c_ushort),
                ("ipv4_addr", ctypes.c_byte * 4),
                ("ipv6_addr", ctypes.c_byte * 16),
                ("__pad2", ctypes.c_ulong),
            ]

        WSAStringToAddressA = ctypes.windll.ws2_32.WSAStringToAddressA
        WSAAddressToStringA = ctypes.windll.ws2_32.WSAAddressToStringA

        def inet_pton(address_family: int, ip_string: str) -> bytes:
            addr = SockAddr()
            ip_string_bytes = ip_string.encode('ascii')
            addr.sa_family = address_family
            addr_size = ctypes.c_int(ctypes.sizeof(addr))

            if WSAStringToAddressA(
                ip_string_bytes, address_family, None,
                ctypes.byref(addr), ctypes.byref(addr_size)
            ) != 0:
                raise socket.error(ctypes.FormatError())

            if address_family == socket.AF_INET:
                return ctypes.string_at(addr.ipv4_addr, 4)
            if address_family == socket.AF_INET6:
                return ctypes.string_at(addr.ipv6_addr, 16)
            raise socket.error('unknown address family')
