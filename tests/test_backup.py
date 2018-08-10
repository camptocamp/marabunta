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
from marabunta.exception import BackupError


# Split runner generation, so we can effortlessly
# change the parameters of backup in tests
@pytest.fixture
def runner_gen(request):
    def runner(parser, config):
        migration = parser.parse()
        table = mock.MagicMock(spec=MigrationTable)
        table.versions.return_value = []
        database = mock.MagicMock(spec=Database)
        return Runner(config, migration, database, table)
    return runner


@pytest.fixture
def parse_yaml(request):
    def parser(filename, allow_serie=True, mode=None):
        migration_file = os.path.join(request.fspath.dirname,
                                      'examples', filename)
        config = Config(migration_file,
                        'test',
                        allow_serie=allow_serie,
                        mode=mode)
        migration_parser = YamlParser.parse_from_file(config.migration_file)
        return migration_parser, config
    return parser


def test_backup(runner_gen, parse_yaml, request, capfd):
    # Simple test that backing up works
    backup_params, config = parse_yaml('migration_with_backup.yml')
    runner = runner_gen(backup_params, config)
    runner.perform()
    expected = (
        u'|> migration: processing version setup\n'
        u'|> version setup: start\n'
        u'|> version setup: Backing up...\n'
        u'backup command\r\n'
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
        u'|> version 0.0.3: Backing up...\n'
        u'backup command\r\n'
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
        u'|> version 0.0.4: Backing up...\n'
        u'backup command\r\n'
        u'|> version 0.0.4: execute base pre-operations\n'
        u'|> version 0.0.4: installation / upgrade of addons\n'
        u'|> version 0.0.4: execute base post-operations\n'
        u'|> version 0.0.4: done\n',
        u''
    )
    assert expected == capfd.readouterr()


def test_backup_ignore_1(runner_gen, parse_yaml, request, capfd):
    # Test that backing up is ignored if ignore_if evaluates to True
    backup_params, config = parse_yaml('migration_with_backup.yml')
    backup_params.parsed['migration']['options']['backup'].update({
        'ignore_if': 'test 1 = 1',
    })
    runner = runner_gen(backup_params, config)
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


def test_backup_ignore_2(runner_gen, parse_yaml, request, capfd):
    # Test that backing up is NOT ignored if no ignore_if set
    backup_params, config = parse_yaml('migration_with_backup.yml')
    backup_params.parsed['migration']['options']['backup'].pop('ignore_if')
    runner = runner_gen(backup_params, config)
    runner.perform()
    expected = (
        u'|> migration: processing version setup\n'
        u'|> version setup: start\n'
        u'|> version setup: Backing up...\n'
        u'backup command\r\n'
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
        u'|> version 0.0.3: Backing up...\n'
        u'backup command\r\n'
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
        u'|> version 0.0.4: Backing up...\n'
        u'backup command\r\n'
        u'|> version 0.0.4: execute base pre-operations\n'
        u'|> version 0.0.4: installation / upgrade of addons\n'
        u'|> version 0.0.4: execute base post-operations\n'
        u'|> version 0.0.4: done\n',
        u''
    )
    assert expected == capfd.readouterr()


def test_backup_stop_on_failure_true(runner_gen, parse_yaml, request, capfd):
    # Test that the migration is failed if stop_on_failure is true and
    # backup command fails
    with pytest.raises(BackupError):
        backup_params, config = parse_yaml('migration_with_backup.yml')
        backup_params.parsed['migration']['options']['backup'].update({
            'command': 'test',
            'args': '1 != 1',
        })
        runner = runner_gen(backup_params, config)
        runner.perform()


def test_backup_no_stop_on_failure(runner_gen, parse_yaml, request, capfd):
    # Test that the migration is failed if stop_on_failure is not specified
    # and backup command fails
    with pytest.raises(BackupError):
        backup_params, config = parse_yaml('migration_with_backup.yml')
        backup_params.parsed['migration']['options']['backup'].update({
            'command': 'test',
            'args': '1 != 1',
        })
        backup_params.parsed['migration']['options']['backup'].pop(
            "stop_on_failure",
        )
        runner = runner_gen(backup_params, config)
        runner.perform()


def test_backup_stop_on_failure_false(runner_gen, parse_yaml, request, capfd):
    # Test that the migration continues if stop_on_failure is false and
    # backup command fails
    backup_params, config = parse_yaml('migration_with_backup.yml')
    backup_params.parsed['migration']['options']['backup'].update({
        'command': 'test',
        'args': '1 != 1',
        'stop_on_failure': False,
    })
    runner = runner_gen(backup_params, config)
    runner.perform()

    expected = (
        u'|> migration: processing version setup\n'
        u'|> version setup: start\n'
        u'|> version setup: Backing up...\n'
        u'|> version setup: Backup command failed! Stop_on_failure is false,'
        u' resuming migration\n'
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
        u'|> version 0.0.3: Backing up...\n'
        u'|> version 0.0.3: Backup command failed! Stop_on_failure is false,'
        u' resuming migration\n'
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
        u'|> version 0.0.4: Backing up...\n'
        u'|> version 0.0.4: Backup command failed! Stop_on_failure is false,'
        u' resuming migration\n'
        u'|> version 0.0.4: execute base pre-operations\n'
        u'|> version 0.0.4: installation / upgrade of addons\n'
        u'|> version 0.0.4: execute base post-operations\n'
        u'|> version 0.0.4: done\n',
        u''
    )
    assert expected == capfd.readouterr()
