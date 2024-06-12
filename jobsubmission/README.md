# Tools for job submission with HTCondor

For testing, you can run `python3 submit_test_job.py`.

While the job is idle or running, you can check its status with `condor_q` and by opening the files
`cjob_submit_test_job_log_<some number>`, `cjob_submit_test_job_out_<some number>`
and `cjob_submit_test_job_err_<some number>`.
Note that on some clusters, the `_out_` and `_err_` files appear only after the job has finished,
while on other clusters they appear already while the job is running and can be used to track the progress of the job.

When the job is finished and if everything went well, you should see "it worked!" in the `_out_` file.
If this is not the case, check the `_err_` and `_log_` files on hints on what went wrong.
If the job finished correctly and you do not need the logs and/or temporary scripts anymore,
you can safely remove them (e.g. with `rm cjob_*`).

### CMSSW version
Some clusters require to load a software environment inside the job.
The easiest way to do this, is by setting a CMSSW environment,
which can be done by passing the `--cmmssw` argument to the test job submitter,
providing it with a path to a CMSSW installation that you would like to use.

Note: if you know of a better way to load software environments in jobs,
that does not require messing about with CMSSW, feel free to make a PR!

### Case study: lxplus
While there may be some dependency on the details of your cluster,
this code was verified to work on lxplus, provided one passes a valid `--cmssw` argument.

Note that job submission from `/eos` does not work on `lxplus`
(see [here](https://batchdocs.web.cern.ch/troubleshooting/eos.html) for more info).
The easiest workaround is to do the job submission from somewhere on `/afs`.
This does not restrict you from using input files and specifying output files somewhere on `/eos`,
only the job itself cannot be submitted from there.
