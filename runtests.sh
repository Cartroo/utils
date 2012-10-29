#!/bin/bash

TOPDIR=$(dirname $(readlink -f $0))
export PYTHONPATH="${PYTHONPATH}:${TOPDIR}/lib:${TOPDIR}/bin"
python -m unittest discover -s ${TOPDIR}/tests -b

