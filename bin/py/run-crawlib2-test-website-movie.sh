#!/bin/bash
# -*- coding: utf-8 -*-

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_bin="$(dirname "${dir_here}")"
dir_project_root=$(dirname "${dir_bin}")

source ${dir_bin}/py/python-env.sh

path_movie_app="${dir_project_root}/example/run_crawlib2_test_website_movie.py"

${bin_python} ${path_movie_app}
