# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os

import pytest

from marabunta.exception import BackupError
from marabunta.model import BackupOperation, Operation, SilentOperation


def test_from_single_unicode():
    op = Operation("ls -l")
    assert op.command == "ls -l"


def test_from_single_str():
    op = Operation("ls -l")
    assert op.command == "ls -l"


def test_from_list_of_unicode():
    op = Operation(["ls", "-l"])
    assert op.command == "ls -l"


def test_from_list_of_str():
    op = Operation(["ls", "-l"])
    assert op.command == "ls -l"


def test_log_execute_output(capfd):
    op = Operation("echo hello world")
    logs = []

    def log(msg, **kwargs):
        logs.append(msg)

    op.execute(log)
    assert logs == ["echo hello world", "hello world"]
    assert capfd.readouterr() == ("hello world\r\n", "")


def test_shell_operation(capfd):
    # must be able to read env. variables
    test = os.environ["PYTEST_CURRENT_TEST"]
    op = Operation("echo $PYTEST_CURRENT_TEST", shell=True)
    logs = []

    def log(msg, **kwargs):
        logs.append(msg)

    op.execute(log)
    assert logs == ["echo $PYTEST_CURRENT_TEST", test]
    assert capfd.readouterr() == (f"{test}\r\n", "")


def test_silent_operation(capfd):
    op = SilentOperation("echo foo")
    op.execute()
    assert capfd.readouterr() == ("", "")


def test_silent_operation_shell(capfd):
    op = SilentOperation("echo foo", shell=True)
    op.execute()
    assert capfd.readouterr() == ("", "")


def test_backup_operation_stop_on_failure(capfd):
    op = BackupOperation("false", stop_on_failure=True)
    with pytest.raises(BackupError):
        op.execute(lambda x: None)


def test_backup_operation_no_stop_on_failure(capfd):
    op = BackupOperation("false", stop_on_failure=False)
    op.execute(lambda x: None)
