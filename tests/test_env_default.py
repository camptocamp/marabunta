from marabunta.config import EnvDefault, BoolEnvDefault

import os


def test_env_default_str():
    os.environ['test_var'] = 'Foo'
    test = EnvDefault('test_var', option_strings='', dest='test_var')
    assert(test.default == 'Foo')


def test_bool_env_default_str():
    os.environ['test_var'] = 'True'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert(test.default)

    os.environ['test_var'] = 'true'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert(test.default)

    os.environ['test_var'] = '1'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert(test.default)

    os.environ['test_var'] = 'False'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert(not test.default)

    os.environ['test_var'] = 'false'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert(not test.default)

    os.environ['test_var'] = '3'
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert(not test.default)

    del os.environ['test_var']
    test = BoolEnvDefault('test_var', option_strings='', dest='test_var')
    assert(not test.default)
