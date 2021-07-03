from proxion.util.common import *


def test_is_proxy_format():
    assert is_proxy_format('0.0.0.0:0') == True
    assert is_proxy_format('255.255.255.255:65535') == True
    assert is_proxy_format(None) == False
    assert is_proxy_format('') == False
    assert is_proxy_format('256.255.255.255:65535') == False
    assert is_proxy_format('255.255.255.255:65536') == False
    assert is_proxy_format('1.1.1.1:-20') == False
    assert is_proxy_format('-1.1.1.1:20') == False
    assert is_proxy_format('a1.1.1.1:20') == False
    assert is_proxy_format('1.1.1.1:20a') == False
    assert is_proxy_format('1.1.1.1:-20') == False


def test_is_ip_addr():
    assert is_ip_address('0.0.0.0') == True
    assert is_ip_address('255.255.255.255') == True
    assert is_ip_address(None) == False
    assert is_ip_address('') == False
    assert is_ip_address('256.255.255.255') == False
    assert is_ip_address('-1.1.1.1') == False
    assert is_ip_address('a1.1.1.1') == False
