#!/bin/bash

set -ex

export FILE_MANAGER_CONFIG='tests/test_config.yaml'

pytest -v tests/