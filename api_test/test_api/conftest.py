# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: conftest.py

# @Software: PyCharm
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--project", action="store", default=1,
        help="project_id"
    )

    parser.addoption(
        "--path", action="store", default=1,
        help="case path"
    )


@pytest.fixture(scope="session", autouse=True)
def project(request):
    return request.config.getoption("--project")


@pytest.fixture(scope="session", autouse=True)
def path(request):
    return request.config.getoption("--path")
