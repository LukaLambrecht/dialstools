#####################
# submit a test job #
#####################


import os
import sys
import argparse
import condortools as ct


def dosomething():
    ### do something in a job
    print('it worked!')


if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cmssw', default=None,
      help='Path to a CMSSW installation (needed on some clusters'
          +' for loading a software environment), default is None.')
    parser.add_argument('-m', '--runmode', choices=['condor','local'], default='condor',
      help='Whether to run in a condor job or locally in the terminal.')
    args = parser.parse_args()

    if args.runmode=='condor':
        cmd = 'python3 submit_test_job.py -m local'
        ct.submitCommandAsCondorJob('cjob_submit_test_job', cmd,
            cmssw_version=args.cmssw)

    elif args.runmode=='local':
        dosomething()
