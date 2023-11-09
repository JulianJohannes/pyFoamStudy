#!/usr/bin/env python
# coding: utf-8

from subprocess import run
from shlex import quote
from argparse import ArgumentParser, RawTextHelpFormatter
import sys
import os.path
import yaml
import json
import pyFoamStudy

app_description = \
"""
Filter out all cases not listes in the study json file.
Default: Get cases from json inside <STUDYDIR>/<STUDYDIR>.info
"""

def parse_arguments():
    parser = ArgumentParser(description=app_description, formatter_class=RawTextHelpFormatter)
    parser.add_argument("STUDYDIR",
                        help="Study directory",
                        default='./'
                        )
    
    args = parser.parse_args()
    assert os.path.isdir(args.STUDYDIR), f"{args.STUDYDIR} is no directory!"
    return args


def rm_cases(cases):
    return run(f"rm -rf {' '.join(cases)}", shell=True).returncode


def main():
    args = parse_arguments()
    basename_studydir = os.path.basename(os.path.abspath(args.STUDYDIR))
    args.infofile = os.path.join(args.STUDYDIR, f"{basename_studydir}.info")
    info = pyFoamStudy.io.read_info(args.infofile)
    
    cases_keep = sorted(pyFoamStudy.io.read_json(os.path.join(args.STUDYDIR, info['json_variationfile'])).keys())
    cases_all = pyFoamStudy.io.read_list(os.path.join(args.STUDYDIR, info['casesfile']))
    cases_rm = sorted(set(cases_all) - set(cases_keep))
    
    status = rm_cases(cases_rm)
    if status == 0:
        print("Removed the cases:")
        print(*cases_rm, sep='\n')
    else:
        print("Removing cases was not successful.")
        sys.exit(status)
    pyFoamStudy.io.write_list(cases_keep, os.path.join(args.STUDYDIR, info['casesfile']))
    

if __name__ == "__main__":
    main()