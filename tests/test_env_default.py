from marabunta.config import EnvDefault, BoolEnvDefault

import os


def test_env_default_str():
    os.environ['test_var'] = 'Foo'
    test = EnvDefault('test_var', option_strings='', dest='test_var')
    assert test.default == 'Foo'


def test_env_default_str_multiple():
    os.environ['test_var_2'] = 'Foo'
    test = EnvDefault(('test_var', 'test_var_2'), option_strings='', dest='test_var')
    assert test.default == 'Foo'


def test_env_default_with_regular_default():
    # Env var is set, so it's used instead of the regular default
    os.environ['test_var_3'] = 'Foo'
    test = EnvDefault('test_var', option_strings='', dest='test_var', default='Bar')
    assert test.default == 'Foo'


def test_env_default_with_regular_default_and_no_env_var():
    # No env var set, so the regular default should be used
    test = EnvDefault('test_var_4', option_strings='', dest='test_var', default='Bar')
    assert test.default == 'Bar'


def test_env_default_with_regular_default_and_no_env_var_and_no_regular_default():
    # No env var set, no regular default, so it should be None
    test = EnvDefault('test_var_5', option_strings='', dest='test_var')
    assert test.default is None


def test_bool_env_default_str():
    os.environ['test_var'] = 'True'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert test.default

    os.environ['test_var'] = 'true'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert test.default

    os.environ['test_var'] = '1'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert test.default

    os.environ['test_var'] = 'False'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert not test.default

    os.environ['test_var'] = 'false'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert not test.default

    os.environ['test_var'] = '3'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert not test.default

    del os.environ['test_var']
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert not test.default
