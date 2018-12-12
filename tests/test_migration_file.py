# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import pytest
import os

import mock

from marabunta.config import Config
from marabunta.database import Database, MigrationTable, VersionRecord
from marabunta.parser import YamlParser
from marabunta.runner import Runner


@pytest.fixture
def runner_gen(request):
    def runner(filename, allow_serie=True, mode=None, db_versions=None):
        migration_file = os.path.join(request.fspath.dirname,
                                      'examples', filename)
        config = Config(migration_file,
                        'test',
                        allow_serie=allow_serie,
                        mode=mode)
        migration_parser = YamlParser.parse_from_file(config.migration_file)
        migration = migration_parser.parse()
        table = mock.MagicMock(spec=MigrationTable)
        table.versions.return_value = db_versions or []
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
        u'|> version setup: echo \'pre-operation\'\n'
        u'pre-operation\r\n'
        u'|> version setup: installation / upgrade of addons\n'
        u'|> version setup: execute base post-operations\n'
        u'|> version setup: echo \'post-operation\'\n'
        u'post-operation\r\n'
        u'|> version setup: done\n'
        u'|> migration: processing version 0.0.2\n'
        u'|> version 0.0.2: start\n'
        u'|> version 0.0.2: version 0.0.2 is a noop\n'
        u'|> version 0.0.2: done\n'
        u'|> migration: processing version 0.0.3\n'
        u'|> version 0.0.3: start\n'
        u'|> version 0.0.3: execute base pre-operations\n'
        u'|> version 0.0.3: echo \'foobar\'\n'
        u'foobar\r\n'
        u'|> version 0.0.3: echo \'foobarbaz\'\n'
        u'foobarbaz\r\n'
        u'|> version 0.0.3: installation / upgrade of addons\n'
        u'|> version 0.0.3: execute base post-operations\n'
        u'|> version 0.0.3: echo \'post-op with unicode é â\'\n'
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
        u'|> version setup: echo \'pre-operation\'\n'
        u'pre-operation\r\n'
        u'|> version setup: execute prod pre-operations\n'
        u'|> version setup: echo \'pre-operation executed only'
        u' when the mode is prod\'\n'
        u'pre-operation executed only when the mode is prod\r\n'
        u'|> version setup: installation / upgrade of addons\n'
        u'|> version setup: execute base post-operations\n'
        u'|> version setup: echo \'post-operation\'\n'
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
        u'|> version 0.0.3: echo \'foobar\'\n'
        u'foobar\r\n'
        u'|> version 0.0.3: echo \'foobarbaz\'\n'
        u'foobarbaz\r\n'
        u'|> version 0.0.3: execute prod pre-operations\n'
        u'|> version 0.0.3: installation / upgrade of addons\n'
        u'|> version 0.0.3: execute base post-operations\n'
        u'|> version 0.0.3: echo \'post-op with unicode é â\'\n'
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
        runner = runner_gen('migration_no_backup.yml')
        runner.perform()
        expected = (
            u'|> migration: processing version 0.0.1\n'
            u'|> version 0.0.1: start\n'
            u'|> version 0.0.1: execute base pre-operations\n'
            u'|> version 0.0.1: echo \'pre-operation\'\n'
            u'pre-operation\r\n'
            u'|> version 0.0.1: installation / upgrade of addons\n'
            u'|> version 0.0.1: execute base post-operations\n'
            u'|> version 0.0.1: echo \'post-operation\'\n'
            u'post-operation\r\n'
            u'|> version 0.0.1: done\n'
            u'|> migration: processing version 0.0.2\n'
            u'|> version 0.0.2: start\n'
            u'|> version 0.0.2: version 0.0.2 is a noop\n'
            u'|> version 0.0.2: done\n'
            u'|> migration: processing version 0.0.3\n'
            u'|> version 0.0.3: start\n'
            u'|> version 0.0.3: execute base pre-operations\n'
            u'|> version 0.0.3: echo \'foobar\'\n'
            u'foobar\r\n'
            u'|> version 0.0.3: echo \'foobarbaz\'\n'
            u'foobarbaz\r\n'
            u'|> version 0.0.3: installation / upgrade of addons\n'
            u'|> version 0.0.3: execute base post-operations\n'
            u'|> version 0.0.3: echo \'post-op with unicode é â\'\n'
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
        runner = runner_gen('migration_no_backup.yml', mode='prod')
        runner.perform()
        expected = (
            u'|> migration: processing version 0.0.1\n'
            u'|> version 0.0.1: start\n'
            u'|> version 0.0.1: execute base pre-operations\n'
            u'|> version 0.0.1: echo \'pre-operation\'\n'
            u'pre-operation\r\n'
            u'|> version 0.0.1: execute prod pre-operations\n'
            u'|> version 0.0.1: echo \'pre-operation executed only'
            u' when the mode is prod\'\n'
            u'pre-operation executed only when the mode is prod\r\n'
            u'|> version 0.0.1: installation / upgrade of addons\n'
            u'|> version 0.0.1: execute base post-operations\n'
            u'|> version 0.0.1: echo \'post-operation\'\n'
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
            u'|> version 0.0.3: echo \'foobar\'\n'
            u'foobar\r\n'
            u'|> version 0.0.3: echo \'foobarbaz\'\n'
            u'foobarbaz\r\n'
            u'|> version 0.0.3: execute prod pre-operations\n'
            u'|> version 0.0.3: installation / upgrade of addons\n'
            u'|> version 0.0.3: execute base post-operations\n'
            u'|> version 0.0.3: echo \'post-op with unicode é â\'\n'
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


def test_mixed_digits_output_mode(runner_gen, request, capfd):
    old_versions = [
        # 'number date_start date_done log addons'
        VersionRecord('11.0.2', '2018-09-01', '2018-09-01', '', ''),
        VersionRecord('11.1.0', '2018-09-02', '2018-09-02', '', ''),
        VersionRecord('11.1.5', '2018-09-03', '2018-09-03', '', ''),
        VersionRecord('11.2.0', '2018-09-04', '2018-09-04', '', ''),
        VersionRecord('11.3.0', '2018-09-05', '2018-09-05', '', ''),
    ]
    runner = runner_gen(
        'migration_mixed_digits.yml', mode='prod', db_versions=old_versions)
    runner.perform()
    expected = (
        u'|> migration: processing version setup',
        u'|> version setup: start',
        u'|> version setup: version setup is a noop',
        u'|> version setup: done',
        u'|> migration: processing version 11.0.2',
        u'|> version 11.0.2: version 11.0.2 is already installed',
        u'|> migration: processing version 11.1.0',
        u'|> version 11.1.0: version 11.1.0 is already installed',
        u'|> migration: processing version 11.1.5',
        u'|> version 11.1.5: version 11.1.5 is already installed',
        u'|> migration: processing version 11.2.0',
        u'|> version 11.2.0: version 11.2.0 is already installed',
        u'|> migration: processing version 11.3.0',
        u'|> version 11.3.0: version 11.3.0 is already installed',
        u'|> migration: processing version 11.0.3.0.1',
        u'|> version 11.0.3.0.1: start',
        u'|> version 11.0.3.0.1: version 11.0.3.0.1 is a noop',
        u'|> version 11.0.3.0.1: done',
    )
    output = capfd.readouterr()  # ease debug
    assert expected == tuple(output.out.splitlines())
