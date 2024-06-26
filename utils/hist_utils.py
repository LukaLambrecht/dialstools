#!/usr/bin/env python
# coding: utf-8

# **A collection of useful basic functions for processing histograms.**  
# 
# Functionality includes:
# - rebinning, cropping and normalization
# - moment calculation
# - averaging over neighbouring histograms
# - smoothing over neighbouring bins


### imports

# external modules
import numpy as np
from sklearn.preprocessing import normalize
import scipy.signal


### cropping of histograms

def crophists(hists, slices=None):
    ### perform cropping on a set of histograms
    # input arguments:
    # - hists: a numpy array of shape (nhistograms,nbins) for 1D or (nhistograms,nybins,nxbins) for 2D
    # - slices: a slice object (builtin python type) or a list of two slices (for 2D)
    #   notes: 
    #     - a slice can be created using the builtin python syntax 'slice(start,stop,step)', 
    #       and the syntax 'list[slice]' is equivalent to 'list[start:stop:step]'.
    #       use 'None' to ignore one of the arguments for slice creation (equivalent to ':' in direct slicing)
    #     - for 1D histograms, slices can be either a slice object or a list of length 1 containing a single slice.
    # returns:
    # - a numpy array containing the same histograms as input but cropped according to the slices argument
    if slices is None: return hists
    if len(hists.shape)==2:
        if isinstance(slices,slice): slices=[slices]
        return hists[:,slices[0]]
    elif len(hists.shape)==3:
        return hists[:,slices[0],slices[1]]
    else:
        raise Exception('ERROR in hist_utils.py / crophists: histograms have invalid input shape: {}'.format(hists.shape))

### rebinning of histograms

def rebinhists(hists, factor=None):
    ### perform rebinning on a set of histograms
    # input arguments:
    # - hists: a numpy array of shape (nhistograms,nbins) for 1D or (nhistograms,nybins,nxbins) for 2D
    # - factor: the rebinning factor (for 1D), or a tuple of (y axis rebinning factor, x axis rebinning factor) (for 2D) 
    #   note: the rebinning applied here is simple summing of bin contents,
    #         and the rebinning factors must be divisors of the respective number of bins!
    # returns:
    # - a numpy array containing the same histograms as input but rebinned according to the factor argument
    if factor is None: return hists
    # case of 1D histograms
    if len(hists.shape)==2:
        if(not hists.shape[1]%factor==0): 
            print('WARNING in hist_utils.py / rebinhists: no rebinning performed since no suitable reduction factor was given.'
                 +' The rebinning factor ({}) is not a divisor of the number of bins ({})'.format(factor,hists.shape[1]))
            return hists
        (nhists,nbins) = hists.shape
        newnbins = int(nbins/factor)
        rebinned = np.zeros((nhists,newnbins))
        for i in range(newnbins):
            rebinned[:,i] = np.sum(hists[:,factor*i:factor*(i+1)],axis=1)
        return rebinned
    # case of 2D histograms
    elif len(hists.shape)==3:
        if( not ((isinstance(factor,tuple) or isinstance(factor,list)) and len(factor)==2) ):
            msg = 'WARNING in hist_utils.py / rebinhists:'
            msg += ' no rebinning performed since no suitable reduction factor was given'
            msg += ' (must be a tuple of length 2 for 2D histograms'
            msg += ' but found {} of type {})'.format(factor,type(factor))
            print(msg)
            return hists
        if( not hists.shape[1]%factor[0]==0 or not hists.shape[2]%factor[1]==0):
            msg = 'WARNING: in hist_utils.py / rebinhists:'
            msg += ' no rebinning performed since no suitable reduction factor was given.'
            msg += ' The rebinning factors ({})'.format(factor)
            msg += ' are not divisors of the number of bins ({})'.format(hists.shape[1:])
            print(msg)
            return hists
        (nhists,nybins,nxbins) = hists.shape
        newnybins = int(nybins/factor[0])
        newnxbins = int(nxbins/factor[1])
        rebinned = np.zeros((nhists,newnybins,newnxbins))
        for i in range(newnybins):
            for j in range(newnxbins):
                rebinned[:,i,j] = np.sum(hists[:,factor[0]*i:factor[0]*(i+1),factor[1]*j:factor[1]*(j+1)],axis=(1,2))
        return rebinned
    else:
        raise Exception('ERROR in hist_utils.py / rebinhists:'
                +' histograms have invalid input shape: {}'.format(hists.shape))

### normalization

def normalizehists(hists):
    ### perform normalization on a set of histograms
    # note: 
    # - for 1D histograms, the sum of bin contents is set equal one for each histogram
    # - for 2D histograms, the bin contents are scaled so the maximum is 1 for each histogram
    # - maybe later make more flexible by adding normalization stragy as argument...
    # input arguments:
    # - hists: a numpy array of shape (nhistograms,nbins) for 1D or (nhistograms,nybins,nxbins) for 2D
    # returns:
    # - a numpy array containing the same histograms as input but normalized
    if len(hists.shape)==2: return normalize(hists, norm='l1', axis=1)
    elif len(hists.shape)==3:
        normhists = []
        for i in range(len(hists)):
            hmax = hists[i].max()
            if hmax==0: hmax = 1
            normhists.append( hists[i]/hmax )
        return np.array(normhists)
    else:
        raise Exception('ERROR in hist_utils.py / normalizehists: histograms have invalid input shape: {}'.format(hists.shape))

### averaging a collection of histograms (e.g. for template definition)

def averagehists(hists, nout=None):
    ### partition a set of histograms into equal parts and take the average histogram of each part
    # input arguments:
    # - hists: a numpy array of shape (nhistograms,nbins) for 1D or (nhistograms,nybins,nxbins) for 2D
    # - nout: number of partitions, i.e. number of output histograms
    #   note: nout=1 corresponds to simply taking the average of all histograms in hists.
    #   note: if nout is negative or if nout is larger than number of input histograms, the original set of histograms is returned.
    # returns:
    # - a numpy array of shape (nout,nbins)
    if nout is None: return hists
    if nout<0: return hists
    if nout > len(hists):
        print('WARNING in hist_utils.py / averagehists: requested number of output histograms ({})'.format(nout)
             +' is larger than number of input histograms ({}),'.format(len(hists))
             +' returning input histograms.')
        return hists
    nsub = int(len(hists)/nout)
    if len(hists.shape)==2:
        avghists = np.zeros((nout,hists.shape[1]))   
        for i in range(nout):
            startindex = i*nsub
            stopindex = (i+1)*nsub
            avghists[i,:] = np.mean(hists[startindex:stopindex,:],axis=0)
        return avghists
    elif len(hists.shape)==3:
        avghists = np.zeros((nout,hists.shape[1],hists.shape[2]))   
        for i in range(nout):
            startindex = i*nsub
            stopindex = (i+1)*nsub
            avghists[i,:] = np.mean(hists[startindex:stopindex,:,:],axis=0)
        return avghists
    else:
        raise Exception('ERROR in hist_utils.py / averagehists: histograms have invalid input shape: {}'.format(hists.shape))
        
def running_average_hists(hists, window=None, weights=None):
    ### replace each histogram in a collection of histograms by its running average
    # input arguments:
    # - hists: a numpy array of shape (nhistograms,nbins) for 1D or (nhistograms,nybins,nxbins) for 2D
    # - window: number of histograms to consider for the averaging
    #   if window is an integer, it is the number of previous histograms in hists used for averaging
    #   (so window=0 would correspond to no averaging)
    #   if window is a tuple, it corresponds to (nprevious,nnext), and the nprevious previous and nnext next histograms in hists are used for averaging
    #   (so window=(0,0) would correspond to no averaging)
    # - weights: a list or numpy array containing the relative weights of the histograms in the averaging procedure.
    #   note: the weights can be any number, but they will be normalized to have unit sum.
    #   note: weights must have length nwindow+1 or nprevious+1+nnext.
    #   note: the default behaviour is a uniform array with values 1./(window+1) (or 1./(nprevious+1+nnext))
    # returns:
    # - a numpy array with same shape as input but where each histogram is replaced by its running average
    # notes:
    # - at the edges, the weights are cropped to match the input array and renormalized
    # - this function will throw an error when the length of the set of histograms is smaller than the total window length,
    #   maybe extend later (although this is not normally needed)
    
    if window is None: return hists
    # check input arguments
    if isinstance(window,int):
        window = (window,0)
    elif len(window)!=2:
        raise Exception('ERROR in hist_utils.py / running_average_hists:'
                +' window argument is invalid: {}'.format(window))
    nwindow = window[0]+window[1]+1
    if weights is None:
        weights = np.ones(nwindow)/nwindow
    elif len(weights)!=nwindow:
        raise Exception('ERROR in hist_utils.py / running_average_hists: weights argument is invalid: '
                       +'found length {} while the window has length {}'.format(len(weights),nwindow))
    avghists = np.zeros(hists.shape)
    weights = normalize([weights], norm='l1')[0]
    # first low edge
    for i in range(len(avghists)):
        hlower = max(i-window[0],0)
        hupper = min(i+1+window[1],len(hists))
        thesehists = hists[hlower:hupper]
        wlower = max(window[0]-i,0)
        wupper = min(len(weights)+len(hists)-window[1]-1-i,len(weights))
        theseweights = normalize([weights[wlower:wupper]], norm='l1')[0]
        avghists[i] = np.average( thesehists, weights=theseweights, axis=0 )
    return avghists

### smoothing

def smoothhists(hists, halfwindow=None, weights=None):
    ### perform histogram smoothing by averaging over neighbouring bins
    # input arguments:
    # - hists: a numpy array of shape (nhistograms, nbins) for 1D
    #          or (nhistograms, nybins, nxbins) for 2D.
    # - halfwindow: number of bins to consider for the averaging;
    #               for 1D histograms, must be an int, corresponding to the number of bins
    #               before and after the current bin to average over;
    #               for 2D histograms, must be a tuple of (halfwindow_y, halfwindow_x).
    # - weights: numpy array containing the relative weights of the bins for the averaging;
    #            for 1D histograms, must have length 2*halfwindow+1;
    #            for 2D histograms, must have shape (2*halfwindow_y+1, 2*halfwindow_x+1).
    #            note: the weights can be any number, but they will be normalized to have unit sum.
    #            note: the default behaviour is a uniform array
    # returns:
    # - a numpy array with same shape as input but where each histogram is replaced 
    #   by its smoothed version

    # check input arguments
    if halfwindow is None: return hists
    # case of 1D histograms
    if len(hists.shape)==2:
        if isinstance(halfwindow,int):
            halfwindow = (0,halfwindow)
        else: raise Exception('ERROR in hist_utils.py / smoothhists:'
                +' halfwindow argument must be an int for 1D histograms.')
        if( weights is not None and len(weights.shape)!=1 ):
            raise Exception('ERROR in hist_utils.py / smoothhists:'
                +' weights argument must be 1D for 1D histograms.')
    # case of 2D histograms
    if len(hists.shape)==3:
        if not (isinstance(halfwindow, tuple) or isinstance(halfwindow, list)):
            raise Exception('ERROR in hist_utils.py / smoothhists:'
                +' halfwindow argument must be a tuple for 2D histograms.')
        if len(halfwindow)!=2:
            raise Exception('ERROR in hist_utils.py / smoothhists:'
                +' halfwindow argument must be a tuple of length 2 for 2D histograms.')
        if( weights is not None and len(weights.shape)!=2 ):
            raise Exception('ERROR in hist_utils.py / smoothhists:'
                +' weights argument must be 2D for 2D histograms.')
    
    # format weights
    windowshape = (2*halfwindow[0]+1, 2*halfwindow[1]+1)
    nwindow = (2*halfwindow[0]+1)*(2*halfwindow[1]+1)
    if weights is None: weights = np.ones(windowshape)/nwindow
    if len(weights.shape)==1: weights = np.expand_dims(weights, axis=0)
    if weights.shape!=(windowshape):
        raise Exception('ERROR in hist_utils.py / smoothhists:'
                +' weights argument is invalid:'
                +' found shape {} while the window has shape {}'.format(weights.shape,windowshape))
    
    # initializations
    smhists = np.zeros(hists.shape)
    weights = weights/np.sum(weights)
    weights = weights[::-1,::-1] # switch order for correct definition in scipy.signal.convolve

    # do the smoothing
    for i,hist in enumerate(hists):
        if len(hist.shape)==1: hist = np.expand_dims(hist, axis=0)
        smhists[i] = scipy.signal.convolve( hist, weights, mode='same' )
    return smhists

### functions for calculating moments of a histogram

def moment(bins, counts, order):
    ### get n-th central moment of a histogram
    # input arguments:
    # - bins: a 1D or 2D np array holding the bin centers
    #   (shape (nbins) or (nhistograms,nbins))
    # - counts: a 2D np array containing the bin counts
    #   (shape (nhistograms,nbins))
    # - order: the order of the moment to calculate
    #   (0 = maximum value, 1 = mean value)
    # returns:
    # - an array of shape (nhistograms) holding the requested moment per histogram
    # notes: 
    # - for now only 1D histograms are supported!
    if len(bins.shape)==1:
        bins = np.tile(bins,(len(counts),1))
    if not bins.shape == counts.shape:
        raise Exception('ERROR in hist_utils.py / moment: bins and counts do not have the same shape!')
    if len(bins.shape)==1:
        bins = np.array([bins])
        counts = np.array([counts])
    if order==0: # return maximum
        return np.nan_to_num(np.max(counts,axis=1))
    ccsum = np.sum(np.multiply(counts,np.power(bins,order)), axis=1, dtype=np.float)
    csum = np.sum(counts, axis=1)
    csumsafe = np.where( csum==0, 1, csum )
    moment = np.where( csum==0, 0, np.nan_to_num(np.divide(ccsum,csumsafe)) )
    return moment

def histmean(bins, counts):
    ### special case of moment calculation (with order=1)
    return moment(bins,counts,1)

def histrms(bins, counts):
    ### special case of moment calculation
    return np.power(moment(bins,counts,2)-np.power(moment(bins,counts,1),2),0.5)

def histmoments(bins, counts, orders):
    ### apply moment calculation for a list of orders
    # input arguments:
    # - see function moment(bins, counts, order),
    #   the only difference being that orders is a list instead of a single number
    # returns:
    # - a numpy array of shape (nhistograms,nmoments)
    moments = np.zeros((len(counts),len(orders)))
    for i,order in enumerate(orders):
        moments[:,i] = moment(bins,counts,order)
    return moments