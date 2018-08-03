# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import pytest
import os

import mock

from marabunta.config import Config
from marabunta.database import Database, MigrationTable
from marabunta.parser import YamlParser
from marabunta.runner import Runner


@pytest.fixture
def runner_gen(request):
    def runner(filename, allow_serie=True, mode=None):
        migration_file = os.path.join(request.fspath.dirname,
                                      'examples', filename)
        config = Config(migration_file,
                        'test',
                        allow_serie=allow_serie,
                        mode=mode)
        migration_parser = YamlParser.parse_from_file(config.migration_file)
        migration = migration_parser.parse()
        table = mock.MagicMock(spec=MigrationTable)
        table.versions.return_value = []
        database = mock.MagicMock(spec=Database)
        return Runner(config, migration, database, table)
    return runner


def test_example_file_output(runner_gen, request, capfd):
    runner = runner_gen('migration.yml')
    runner.perform()
    expected = (
        u'|> migration: processing version setup\n'
        u'|> version setup: start\n'
        u'|> version setup: execute base pre-operations\n'
        u'|> version setup: echo pre-operation\n'
        u'pre-operation\r\n'
        u'|> version setup: installation / upgrade of addons\n'
        u'|> version setup: execute base post-operations\n'
        u'|> version setup: echo post-operation\n'
        u'post-operation\r\n'
        u'|> version setup: done\n'
        u'|> migration: processing version 0.0.2\n'
        u'|> version 0.0.2: start\n'
        u'|> version 0.0.2: version 0.0.2 is a noop\n'
        u'|> version 0.0.2: done\n'
        u'|> migration: processing version 0.0.3\n'
        u'|> version 0.0.3: start\n'
        u'|> version 0.0.3: execute base pre-operations\n'
        u'|> version 0.0.3: echo foobar\n'
        u'foobar\r\n'
        u'|> version 0.0.3: echo foobarbaz\n'
        u'foobarbaz\r\n'
        u'|> version 0.0.3: installation / upgrade of addons\n'
        u'|> version 0.0.3: execute base post-operations\n'
        u'|> version 0.0.3: echo post-op with unicode é â\n'
        u'post-op with unicode é â\r\n'
        u'|> version 0.0.3: done\n'
        u'|> migration: processing version 0.0.4\n'
        u'|> version 0.0.4: start\n'
        u'|> version 0.0.4: version 0.0.4 is a noop\n'
        u'|> version 0.0.4: done\n',
        u''
    )
    assert expected == capfd.readouterr()


def test_example_file_output_mode(runner_gen, request, capfd):
    runner = runner_gen('migration.yml', mode='prod')
    runner.perform()
    expected = (
        u'|> migration: processing version setup\n'
        u'|> version setup: start\n'
        u'|> version setup: execute base pre-operations\n'
        u'|> version setup: echo pre-operation\n'
        u'pre-operation\r\n'
        u'|> version setup: execute prod pre-operations\n'
        u'|> version setup: echo pre-operation executed only'
        u' when the mode is prod\n'
        u'pre-operation executed only when the mode is prod\r\n'
        u'|> version setup: installation / upgrade of addons\n'
        u'|> version setup: execute base post-operations\n'
        u'|> version setup: echo post-operation\n'
        u'post-operation\r\n'
        u'|> version setup: execute prod post-operations\n'
        u'|> version setup: done\n'
        u'|> migration: processing version 0.0.2\n'
        u'|> version 0.0.2: start\n'
        u'|> version 0.0.2: version 0.0.2 is a noop\n'
        u'|> version 0.0.2: done\n'
        u'|> migration: processing version 0.0.3\n'
        u'|> version 0.0.3: start\n'
        u'|> version 0.0.3: execute base pre-operations\n'
        u'|> version 0.0.3: echo foobar\n'
        u'foobar\r\n'
        u'|> version 0.0.3: echo foobarbaz\n'
        u'foobarbaz\r\n'
        u'|> version 0.0.3: execute prod pre-operations\n'
        u'|> version 0.0.3: installation / upgrade of addons\n'
        u'|> version 0.0.3: execute base post-operations\n'
        u'|> version 0.0.3: echo post-op with unicode é â\n'
        u'post-op with unicode é â\r\n'
        u'|> version 0.0.3: execute prod post-operations\n'
        u'|> version 0.0.3: done\n'
        u'|> migration: processing version 0.0.4\n'
        u'|> version 0.0.4: start\n'
        u'|> version 0.0.4: version 0.0.4 is a noop\n'
        u'|> version 0.0.4: done\n',
        u''
    )
    assert expected == capfd.readouterr()


def test_example_no_setup_file_output(runner_gen, request, capfd):
    with pytest.warns(FutureWarning) as record:
        runner = runner_gen('migration_no_setup.yml')
        runner.perform()
        expected = (
            u'|> migration: processing version 0.0.1\n'
            u'|> version 0.0.1: start\n'
            u'|> version 0.0.1: execute base pre-operations\n'
            u'|> version 0.0.1: echo pre-operation\n'
            u'pre-operation\r\n'
            u'|> version 0.0.1: installation / upgrade of addons\n'
            u'|> version 0.0.1: execute base post-operations\n'
            u'|> version 0.0.1: echo post-operation\n'
            u'post-operation\r\n'
            u'|> version 0.0.1: done\n'
            u'|> migration: processing version 0.0.2\n'
            u'|> version 0.0.2: start\n'
            u'|> version 0.0.2: version 0.0.2 is a noop\n'
            u'|> version 0.0.2: done\n'
            u'|> migration: processing version 0.0.3\n'
            u'|> version 0.0.3: start\n'
            u'|> version 0.0.3: execute base pre-operations\n'
            u'|> version 0.0.3: echo foobar\n'
            u'foobar\r\n'
            u'|> version 0.0.3: echo foobarbaz\n'
            u'foobarbaz\r\n'
            u'|> version 0.0.3: installation / upgrade of addons\n'
            u'|> version 0.0.3: execute base post-operations\n'
            u'|> version 0.0.3: echo post-op with unicode é â\n'
            u'post-op with unicode é â\r\n'
            u'|> version 0.0.3: done\n'
            u'|> migration: processing version 0.0.4\n'
            u'|> version 0.0.4: start\n'
            u'|> version 0.0.4: version 0.0.4 is a noop\n'
            u'|> version 0.0.4: done\n',
            u''
        )
        assert expected == capfd.readouterr()

    assert 1 == len(record)
    warnings_msg = u'First version should be named `setup`'
    assert warnings_msg == record[0].message.args[0]


def test_example_no_setup_file_output_mode(runner_gen, request, capfd):
    with pytest.warns(FutureWarning) as record:
        runner = runner_gen('migration_no_setup.yml', mode='prod')
        runner.perform()
        expected = (
            u'|> migration: processing version 0.0.1\n'
            u'|> version 0.0.1: start\n'
            u'|> version 0.0.1: execute base pre-operations\n'
            u'|> version 0.0.1: echo pre-operation\n'
            u'pre-operation\r\n'
            u'|> version 0.0.1: execute prod pre-operations\n'
            u'|> version 0.0.1: echo pre-operation executed only'
            u' when the mode is prod\n'
            u'pre-operation executed only when the mode is prod\r\n'
            u'|> version 0.0.1: installation / upgrade of addons\n'
            u'|> version 0.0.1: execute base post-operations\n'
            u'|> version 0.0.1: echo post-operation\n'
            u'post-operation\r\n'
            u'|> version 0.0.1: execute prod post-operations\n'
            u'|> version 0.0.1: done\n'
            u'|> migration: processing version 0.0.2\n'
            u'|> version 0.0.2: start\n'
            u'|> version 0.0.2: version 0.0.2 is a noop\n'
            u'|> version 0.0.2: done\n'
            u'|> migration: processing version 0.0.3\n'
            u'|> version 0.0.3: start\n'
            u'|> version 0.0.3: execute base pre-operations\n'
            u'|> version 0.0.3: echo foobar\n'
            u'foobar\r\n'
            u'|> version 0.0.3: echo foobarbaz\n'
            u'foobarbaz\r\n'
            u'|> version 0.0.3: execute prod pre-operations\n'
            u'|> version 0.0.3: installation / upgrade of addons\n'
            u'|> version 0.0.3: execute base post-operations\n'
            u'|> version 0.0.3: echo post-op with unicode é â\n'
            u'post-op with unicode é â\r\n'
            u'|> version 0.0.3: execute prod post-operations\n'
            u'|> version 0.0.3: done\n'
            u'|> migration: processing version 0.0.4\n'
            u'|> version 0.0.4: start\n'
            u'|> version 0.0.4: version 0.0.4 is a noop\n'
            u'|> version 0.0.4: done\n',
            u''
        )
        assert expected == capfd.readouterr()

    assert 1 == len(record)
    warnings_msg = u'First version should be named `setup`'
    assert warnings_msg == record[0].message.args[0]
