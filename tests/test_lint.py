from subprocess import call


def test_lint():
    assert 0 == call(
        ['flake8', '--max-line-length=110', '--ignore=F401', './proxion/'])
    assert 0 == call(['pylint', '-E', './proxion/'])
