# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pathlib import Path
from unittest import mock

import pytest

from marabunta.config import Config
from marabunta.database import Database, MigrationTable, VersionRecord
from marabunta.exception import MigrationError
from marabunta.parser import YamlParser
from marabunta.runner import Runner


@pytest.fixture
def runner_gen(request):
    def runner(filename, allow_serie=True, mode=None, db_versions=None):
        migration_file = str(Path(request.fspath.dirname) / "examples" / filename)
        config = Config(migration_file, "test", allow_serie=allow_serie, mode=mode)
        migration_parser = YamlParser.parse_from_file(config.migration_file)
        migration = migration_parser.parse()
        table = mock.MagicMock(spec=MigrationTable)
        table.versions.return_value = db_versions or []
        database = mock.MagicMock(spec=Database)
        return Runner(config, migration, database, table)

    return runner


def test_example_file_output(runner_gen, request, capfd):
    runner = runner_gen("migration.yml")
    runner.perform()
    expected = (
        "|> migration: processing version setup\n"
        "|> version setup: start\n"
        "|> version setup: execute base pre-operations\n"
        "|> version setup: echo 'pre-operation'\n"
        "pre-operation\r\n"
        "|> version setup: installation / upgrade of addons\n"
        "|> version setup: execute base post-operations\n"
        "|> version setup: echo 'post-operation'\n"
        "post-operation\r\n"
        "|> version setup: done\n"
        "|> migration: processing version 0.0.2\n"
        "|> version 0.0.2: start\n"
        "|> version 0.0.2: version 0.0.2 is a noop\n"
        "|> version 0.0.2: done\n"
        "|> migration: processing version 0.0.3\n"
        "|> version 0.0.3: start\n"
        "|> version 0.0.3: execute base pre-operations\n"
        "|> version 0.0.3: echo 'foobar'\n"
        "foobar\r\n"
        "|> version 0.0.3: echo 'foobarbaz'\n"
        "foobarbaz\r\n"
        "|> version 0.0.3: installation / upgrade of addons\n"
        "|> version 0.0.3: execute base post-operations\n"
        "|> version 0.0.3: echo 'post-op with unicode é â'\n"
        "post-op with unicode é â\r\n"
        "|> version 0.0.3: done\n"
        "|> migration: processing version 0.0.4\n"
        "|> version 0.0.4: start\n"
        "|> version 0.0.4: version 0.0.4 is a noop\n"
        "|> version 0.0.4: done\n",
        "",
    )
    assert expected == capfd.readouterr()


def test_example_file_output_mode(runner_gen, request, capfd):
    runner = runner_gen("migration.yml", mode="full")
    runner.perform()
    expected = (
        "|> migration: processing version setup\n"
        "|> version setup: start\n"
        "|> version setup: execute base pre-operations\n"
        "|> version setup: echo 'pre-operation'\n"
        "pre-operation\r\n"
        "|> version setup: execute full pre-operations\n"
        "|> version setup: echo 'pre-operation executed only"
        " when the mode is full'\n"
        "pre-operation executed only when the mode is full\r\n"
        "|> version setup: installation / upgrade of addons\n"
        "|> version setup: execute base post-operations\n"
        "|> version setup: echo 'post-operation'\n"
        "post-operation\r\n"
        "|> version setup: execute full post-operations\n"
        "|> version setup: done\n"
        "|> migration: processing version 0.0.2\n"
        "|> version 0.0.2: start\n"
        "|> version 0.0.2: version 0.0.2 is a noop\n"
        "|> version 0.0.2: done\n"
        "|> migration: processing version 0.0.3\n"
        "|> version 0.0.3: start\n"
        "|> version 0.0.3: execute base pre-operations\n"
        "|> version 0.0.3: echo 'foobar'\n"
        "foobar\r\n"
        "|> version 0.0.3: echo 'foobarbaz'\n"
        "foobarbaz\r\n"
        "|> version 0.0.3: execute full pre-operations\n"
        "|> version 0.0.3: installation / upgrade of addons\n"
        "|> version 0.0.3: execute base post-operations\n"
        "|> version 0.0.3: echo 'post-op with unicode é â'\n"
        "post-op with unicode é â\r\n"
        "|> version 0.0.3: execute full post-operations\n"
        "|> version 0.0.3: done\n"
        "|> migration: processing version 0.0.4\n"
        "|> version 0.0.4: start\n"
        "|> version 0.0.4: version 0.0.4 is a noop\n"
        "|> version 0.0.4: done\n",
        "",
    )
    assert expected == capfd.readouterr()


def test_example_no_setup_file_output(runner_gen, request, capfd):
    msg = "First version should be named `setup`"
    with pytest.warns(FutureWarning, match=msg):
        runner = runner_gen("migration_no_backup.yml")
        runner.perform()
        expected = (
            "|> migration: processing version 0.0.1\n"
            "|> version 0.0.1: start\n"
            "|> version 0.0.1: execute base pre-operations\n"
            "|> version 0.0.1: echo 'pre-operation'\n"
            "pre-operation\r\n"
            "|> version 0.0.1: installation / upgrade of addons\n"
            "|> version 0.0.1: execute base post-operations\n"
            "|> version 0.0.1: echo 'post-operation'\n"
            "post-operation\r\n"
            "|> version 0.0.1: done\n"
            "|> migration: processing version 0.0.2\n"
            "|> version 0.0.2: start\n"
            "|> version 0.0.2: version 0.0.2 is a noop\n"
            "|> version 0.0.2: done\n"
            "|> migration: processing version 0.0.3\n"
            "|> version 0.0.3: start\n"
            "|> version 0.0.3: execute base pre-operations\n"
            "|> version 0.0.3: echo 'foobar'\n"
            "foobar\r\n"
            "|> version 0.0.3: echo 'foobarbaz'\n"
            "foobarbaz\r\n"
            "|> version 0.0.3: installation / upgrade of addons\n"
            "|> version 0.0.3: execute base post-operations\n"
            "|> version 0.0.3: echo 'post-op with unicode é â'\n"
            "post-op with unicode é â\r\n"
            "|> version 0.0.3: done\n"
            "|> migration: processing version 0.0.4\n"
            "|> version 0.0.4: start\n"
            "|> version 0.0.4: version 0.0.4 is a noop\n"
            "|> version 0.0.4: done\n",
            "",
        )
        assert expected == capfd.readouterr()


def test_example_no_setup_file_output_mode(runner_gen, request, capfd):
    msg = "First version should be named `setup`"
    with pytest.warns(FutureWarning, match=msg):
        runner = runner_gen("migration_no_backup.yml", mode="full")
        runner.perform()
        expected = (
            "|> migration: processing version 0.0.1\n"
            "|> version 0.0.1: start\n"
            "|> version 0.0.1: execute base pre-operations\n"
            "|> version 0.0.1: echo 'pre-operation'\n"
            "pre-operation\r\n"
            "|> version 0.0.1: execute full pre-operations\n"
            "|> version 0.0.1: echo 'pre-operation executed only"
            " when the mode is full'\n"
            "pre-operation executed only when the mode is full\r\n"
            "|> version 0.0.1: installation / upgrade of addons\n"
            "|> version 0.0.1: execute base post-operations\n"
            "|> version 0.0.1: echo 'post-operation'\n"
            "post-operation\r\n"
            "|> version 0.0.1: execute full post-operations\n"
            "|> version 0.0.1: done\n"
            "|> migration: processing version 0.0.2\n"
            "|> version 0.0.2: start\n"
            "|> version 0.0.2: version 0.0.2 is a noop\n"
            "|> version 0.0.2: done\n"
            "|> migration: processing version 0.0.3\n"
            "|> version 0.0.3: start\n"
            "|> version 0.0.3: execute base pre-operations\n"
            "|> version 0.0.3: echo 'foobar'\n"
            "foobar\r\n"
            "|> version 0.0.3: echo 'foobarbaz'\n"
            "foobarbaz\r\n"
            "|> version 0.0.3: execute full pre-operations\n"
            "|> version 0.0.3: installation / upgrade of addons\n"
            "|> version 0.0.3: execute base post-operations\n"
            "|> version 0.0.3: echo 'post-op with unicode é â'\n"
            "post-op with unicode é â\r\n"
            "|> version 0.0.3: execute full post-operations\n"
            "|> version 0.0.3: done\n"
            "|> migration: processing version 0.0.4\n"
            "|> version 0.0.4: start\n"
            "|> version 0.0.4: version 0.0.4 is a noop\n"
            "|> version 0.0.4: done\n",
            "",
        )
        assert expected == capfd.readouterr()


def test_mixed_digits_output_mode(runner_gen, request, capfd):
    old_versions = [
        # 'number date_start date_done log addons'
        VersionRecord("11.0.2", "2018-09-01", "2018-09-01", "", ""),
        VersionRecord("11.1.0", "2018-09-02", "2018-09-02", "", ""),
        VersionRecord("11.1.5", "2018-09-03", "2018-09-03", "", ""),
        VersionRecord("11.2.0", "2018-09-04", "2018-09-04", "", ""),
        VersionRecord("11.3.0", "2018-09-05", "2018-09-05", "", ""),
    ]
    runner = runner_gen(
        "migration_mixed_digits.yml", mode="full", db_versions=old_versions
    )
    runner.perform()
    expected = (
        "|> migration: processing version setup",
        "|> version setup: start",
        "|> version setup: version setup is a noop",
        "|> version setup: done",
        "|> migration: processing version 11.0.2",
        "|> version 11.0.2: version 11.0.2 is already installed",
        "|> migration: processing version 11.1.0",
        "|> version 11.1.0: version 11.1.0 is already installed",
        "|> migration: processing version 11.1.5",
        "|> version 11.1.5: version 11.1.5 is already installed",
        "|> migration: processing version 11.2.0",
        "|> version 11.2.0: version 11.2.0 is already installed",
        "|> migration: processing version 11.3.0",
        "|> version 11.3.0: version 11.3.0 is already installed",
        "|> migration: processing version 11.0.0.3.1",
        "|> version 11.0.0.3.1: start",
        "|> version 11.0.0.3.1: version 11.0.0.3.1 is a noop",
        "|> version 11.0.0.3.1: done",
        "|> migration: processing version 11.0.0.3.2",
        "|> version 11.0.0.3.2: start",
        "|> version 11.0.0.3.2: version 11.0.0.3.2 is a noop",
        "|> version 11.0.0.3.2: done",
        "|> migration: processing version 11.0.1.0.0",
        "|> version 11.0.1.0.0: start",
        "|> version 11.0.1.0.0: version 11.0.1.0.0 is a noop",
        "|> version 11.0.1.0.0: done",
        "|> migration: processing version 11.0.2.0.0",
        "|> version 11.0.2.0.0: start",
        "|> version 11.0.2.0.0: version 11.0.2.0.0 is a noop",
        "|> version 11.0.2.0.0: done",
    )
    output = capfd.readouterr()  # ease debug
    assert expected == tuple(output.out.splitlines())


def test_mixed_digits_output_mode2(runner_gen, request, capfd):
    # migrate 1st one 3 digit version then a 5 digit one
    old_versions = [
        # 'number date_start date_done log addons'
        VersionRecord("10.17.0", "2018-09-06", "2018-09-06", "", ""),
    ]
    runner = runner_gen(
        "migration_mixed_digits2.yml", mode="full", db_versions=old_versions
    )
    runner.perform()
    expected = (
        "|> migration: processing version setup",
        "|> version setup: start",
        "|> version setup: version setup is a noop",
        "|> version setup: done",
        "|> migration: processing version 10.17.0",
        "|> version 10.17.0: version 10.17.0 is already installed",
        "|> migration: processing version 10.17.1",
        "|> version 10.17.1: start",
        "|> version 10.17.1: version 10.17.1 is a noop",
        "|> version 10.17.1: done",
        "|> migration: processing version 10.0.0.18.0",
        "|> version 10.0.0.18.0: start",
        "|> version 10.0.0.18.0: version 10.0.0.18.0 is a noop",
        "|> version 10.0.0.18.0: done",
        "|> migration: processing version 10.0.0.19.0",
        "|> version 10.0.0.19.0: start",
        "|> version 10.0.0.19.0: version 10.0.0.19.0 is a noop",
        "|> version 10.0.0.19.0: done",
    )
    output = capfd.readouterr()  # ease debug
    assert expected == tuple(output.out.splitlines())


# All other tests already rely on allow series working when set to true.
# so we only have one test making sure it doesn't work if it is set false.
def test_allow_series_false(runner_gen, request, capfd):
    runner = runner_gen("migration.yml", allow_serie=False)
    with pytest.raises(
        MigrationError, match=r"[.]*Only one version can be upgraded at a time.[.]*"
    ):
        runner.perform()
