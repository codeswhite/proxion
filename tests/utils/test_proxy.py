from proxion.util.proxy import *
from pytest import raises


def test_assure_proxy_format():
    with raises(InvalidProxyFormatError):
        assure_proxy_format(None)

    assert assure_proxy_format('1.1.1.1:222') is None


def test_proxy():
    # init
    p = Proxy('1.1.1.1:80')
    assert p.pip == '1.1.1.1:80'

    t = time()
    p2 = Proxy('1.1.1.1:80', ['http', 'https'], t, 90, 'TEST')
    assert p2.last_check == t
    assert p2.last_lat == 90
    assert p2.exit_country == 'TEST'
    assert all([i for i in p2.protos if i in ['http', 'https']])

    # update
    with raises(ValueError):
        p.update(Proxy('2.2.2.2:442'))

    p.update(p2)
    assert all([i for i in p.protos if i in ['http', 'https']])
    assert p.exit_country == p2.exit_country
    assert p.last_check == p2.last_check
    assert p.last_lat == p2.last_lat

    # serialize
    d = p.serialize()
    assert list(d.keys())[0] == p.pip
    items = d[p.pip]
    assert all([i for i in ['http', 'https'] if i in items['protos']])
    assert items['last_lat'] == p.last_lat
    assert items['last_check'] == p.last_check
    assert items['exit_country'] == p.exit_country

# TODO add test_parse_file