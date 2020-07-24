# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import os
import pytest

import mock

from marabunta.config import Config
from marabunta.database import Database, MigrationTable
from marabunta.model import MigrationBackupOption
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
        u'|> migration: Backing up...\n'
        u'backup command\r\n'
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
        u'|> version 0.0.4: done\n'
    )
    out = capfd.readouterr().out
    assert expected == out


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
        u'|> version 0.0.4: done\n'
    )
    out = capfd.readouterr().out
    assert expected == out


def test_backup_ignore_2(runner_gen, parse_yaml, request, capfd):
    # Test that backing up is NOT ignored if no ignore_if set
    backup_params, config = parse_yaml('migration_with_backup.yml')
    backup_params.parsed['migration']['options']['backup'].pop('ignore_if')
    runner = runner_gen(backup_params, config)
    runner.perform()
    expected = (
        u'|> migration: Backing up...\n'
        u'backup command\r\n'
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
        u'|> version 0.0.4: done\n'
    )
    out = capfd.readouterr().out
    assert expected == out


def test_backup_ignore_3(runner_gen, parse_yaml, request, capfd):
    # Test that backing up is ignored if ignore_if evaluates to True
    # and MARABUNTA_FORCE_VERSION is set
    backup_params, config = parse_yaml('migration_with_backup.yml')
    backup_params.parsed['migration']['options']['backup'].update({
        'ignore_if': 'test -z "$UNKNOWN_VAR"',
    })
    config.force_version = "0.0.4"
    runner = runner_gen(backup_params, config)
    runner.perform()
    expected = (
        u'|> migration: force-execute version 0.0.4\n'
        u'|> migration: processing version 0.0.4\n'
        u'|> version 0.0.4: start\n'
        u'|> version 0.0.4: version 0.0.4 is a noop\n'
        u'|> version 0.0.4: done\n'
    )
    out = capfd.readouterr().out
    assert expected == out


def test_backup_stop_on_failure_true(runner_gen, parse_yaml, request, capfd):
    # Test that the migration is failed if stop_on_failure is true and
    # backup command fails
    with pytest.raises(BackupError):
        backup_params, config = parse_yaml('migration_with_backup.yml')
        backup_params.parsed['migration']['options']['backup'].update({
            'command': 'test 1 != 1',
        })
        runner = runner_gen(backup_params, config)
        runner.perform()


def test_backup_no_stop_on_failure(runner_gen, parse_yaml, request, capfd):
    # Test that the migration is failed if stop_on_failure is not specified
    # and backup command fails
    with pytest.raises(BackupError):
        backup_params, config = parse_yaml('migration_with_backup.yml')
        backup_params.parsed['migration']['options']['backup'].update({
            'command': 'test 1 != 1',
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
        'command': 'test 1 != 1',
        'stop_on_failure': False,
    })
    runner = runner_gen(backup_params, config)
    runner.perform()

    expected = (
        u'|> migration: Backing up...\n'
        u'|> migration: Backup command failed, ignored by configuration.'
        u' Resuming migration\n'
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
        u'|> version 0.0.4: done\n'
    )
    out = capfd.readouterr().out
    assert expected == out


def test_backup_noop(runner_gen, parse_yaml, request, capfd):
    # Test that backup is triggered when noop version has explicit backup=true
    backup_params, config = parse_yaml('migration_with_backup.yml')
    # set all migration steps to backup false except the last one
    for version in backup_params.parsed['migration']['versions']:
        if version['version'] not in ['0.0.4', '0.0.2']:
            version['backup'] = False
    runner = runner_gen(backup_params, config)
    runner.perform()

    expected = (
        u'|> migration: Backing up...\n'
        u'backup command\r\n'
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
        u'|> version 0.0.4: done\n'
    )
    out = capfd.readouterr().out
    assert expected == out


@pytest.fixture
def placeholders_config():
    database = 'a_db'
    db_user = 'a_user'
    db_password = 'a_password'
    db_port = 'a_port'
    db_host = 'a_host'
    return Config(
        'migration.yml',
        database,
        db_user=db_user,
        db_password=db_password,
        db_port=db_port,
        db_host=db_host,
    )


def test_backup_command_placeholders(placeholders_config):
    # all parameters are substituted
    options = MigrationBackupOption(
        'echo $database $db_user $db_password $db_host $db_port',
        'test 1 != 1',
    )
    operation = options.command_operation(placeholders_config)
    assert operation.command == (
        'echo a_db a_user a_password a_host a_port'
    )


def test_backup_command_placeholders_extra(placeholders_config):
    # extra parameters are ignored
    options = MigrationBackupOption(
        'echo $database $db_user $db_password $db_host $db_port $foo',
        'test 1 != 1',
    )
    operation = options.command_operation(placeholders_config)
    assert operation.command == (
        'echo a_db a_user a_password a_host a_port $foo'
    )


def test_backup_command_placeholders_missing(placeholders_config):
    # no failure if not using all placeholders
    options = MigrationBackupOption(
        'echo $database',
        'test 1 != 1',
    )
    operation = options.command_operation(placeholders_config)
    assert operation.command == (
        'echo a_db'
    )


def test_backup_force_version(runner_gen, parse_yaml, request, capfd):
    # Test that backup is triggered when using force_version
    backup_params, config = parse_yaml('migration_with_backup.yml')
    config.force_version = '0.0.3'
    runner = runner_gen(backup_params, config)
    runner.perform()
    expected = (
        u'|> migration: Backing up...\n'
        u'backup command\r\n'
        u'|> migration: force-execute version 0.0.3\n'
        u'|> migration: processing version 0.0.3\n'
        u'|> version 0.0.3: start\n'
        u'|> version 0.0.3: execute base pre-operations\n'
        u"|> version 0.0.3: echo 'foobar'\n"
        u'foobar\r\n'
        u"|> version 0.0.3: echo 'foobarbaz'\n"
        u'foobarbaz\r\n'
        u'|> version 0.0.3: installation / upgrade of addons\n'
        u'|> version 0.0.3: execute base post-operations\n'
        u"|> version 0.0.3: echo 'post-op with unicode é â'\n"
        u'post-op with unicode é â\r\n'
        u'|> version 0.0.3: done\n'
    )
    out = capfd.readouterr().out
    assert expected == out


def test_backup_force_version_no_backup_command(runner_gen, parse_yaml,
                                                request, capfd):
    # Test that backup is not triggered when using force_version but no backup
    # command is configured
    backup_params, config = parse_yaml('migration_no_backup.yml')
    config.force_version = '0.0.3'
    runner = runner_gen(backup_params, config)
    runner.perform()
    expected = (
        u'|> migration: force-execute version 0.0.3\n'
        u'|> migration: processing version 0.0.3\n'
        u'|> version 0.0.3: start\n'
        u'|> version 0.0.3: execute base pre-operations\n'
        u"|> version 0.0.3: echo 'foobar'\n"
        u'foobar\r\n'
        u"|> version 0.0.3: echo 'foobarbaz'\n"
        u'foobarbaz\r\n'
        u'|> version 0.0.3: installation / upgrade of addons\n'
        u'|> version 0.0.3: execute base post-operations\n'
        u"|> version 0.0.3: echo 'post-op with unicode é â'\n"
        u'post-op with unicode é â\r\n'
        u'|> version 0.0.3: done\n'
    )
    out = capfd.readouterr().out
    assert expected == out
