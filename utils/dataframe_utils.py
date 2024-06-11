#!/usr/bin/env python
# coding: utf-8

# **A collection of useful basic functions for manipulating pandas dataframes.**  
# 
# Functionality includes (among others):
# - selecting DCS-bit on data or golden json data.
# - selecting specific runs, lumisections, or types of histograms


### imports

# external modules
import os
import json
import pandas as pd
import numpy as np

# local modules
import json_utils


# getter and selector for histogram names 

def get_menames(df, menamecolumn='me'):
    ### get a list of (unique) ME names present in a df
    # df is a dataframe read from an input csv file.
    menamelist = sorted(list(set(df[menamecolumn].values)))
    return menamelist
    
def select_menames(df, menames, menamecolumn='me'):
    ### keep only a subset of MEs in a df
    # menames is a list of ME names to keep in the df.
    df = df[df[menamecolumn].isin(menames)]
    df.reset_index(drop=True, inplace=True)
    return df


# getter and selector for run numbers

def get_runs(df, runcolumn='run_number'):
    ### return a list of (unique) run numbers present in a df
    # df is a dataframe read from an input csv file.
    runlist = sorted(list(set(df[runcolumn].values)))
    return runlist

def select_runs(df, runnbs, runcolumn='run_number'):
    ### keep only a subset of runs in a df
    # runnbs is a list of run numbers to keep in the df.
    df = df[df[runcolumn].isin(runnbs)]
    df.reset_index(drop=True, inplace=True)
    return df


# getter and selector for lumisection numbers

def get_ls(df, lumicolumn='ls_number'):
    ### return a list of ls numbers present in a df
    # note: the numbers are not required to be unique!
    # note: no check is done on the run number!
    lslist = sorted(list(df[lumicolumn].values))
    return lslist

def select_ls(df, lsnbs, lumicolumn='ls_number'):
    ### keep only a subset of lumisection numbers in a df
    # lsnbs is a list of lumisection numbers to keep in the df.
    # note: no check is done on the run number!
    df = df[df[lumicolumn].isin(lsnbs)]
    df.reset_index(drop=True, inplace=True)
    return df


### general getter and selector in json format

def get_runsls(df, runcolumn='run_number', lumicolumn='ls_number'):
    ### return a dictionary with runs and lumisections in a dataframe (same format as e.g. golden json)
    runslslist = get_runs(df, runcolum=runcolumn)
    for i,run in enumerate(runslslist):
        runslslist[i] = (run, get_ls( select_runs(df,[run],runcolumn=runcolumn), lumicolumn=lumicolumn))
    return json_utils.tuplelist_to_jsondict( runslslist )

def select_json(df, jsonfile, runcolumn='run_number', lumicolumn='ls_number'):
    ### keep only lumisections that are in the given json file
    dfres = df[ json_utils.injson( df[runcolumn].values, df[lumicolumn].values, jsonfile=jsonfile) ]
    dfres.reset_index(drop=True, inplace=True)
    return dfres

def select_runsls(df, jsondict, runcolumn='run_number', lumicolumn='ls_number'):
    ### equivalent to select_json but using a pre-loaded json dict instead of a json file on disk
    dfres = df[ json_utils.injson( df[runcolumn].values, df[lumicolumn].values, jsondict=jsondict) ]
    dfres.reset_index(drop=True, inplace=True)
    return dfres