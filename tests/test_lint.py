from subprocess import call


def test_lint_flake8():
    assert 0 == call(
        ['flake8', '--max-line-length=110', '--ignore=F401', './proxion/'])


def test_lint_pylint():
    assert 0 == call(['pylint', '-E', './proxion/'])
