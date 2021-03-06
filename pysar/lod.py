#! /usr/bin/env python2
############################################################
# Program is part of PySAR v1.2                            #
# Copyright(c) 2013, Heresh Fattahi                        #
# Author:  Heresh Fattahi                                  #
############################################################

#########################################################################################
#                                                                                       #
# The empiriocal model in this program to correct the Local Oscilator Frequency Decay   #
# of Envisat ASAR instrument was suggested by Petar Marinkovic and Yngvar Larsen, 2013. #
#                                                                                       #
#########################################################################################
# Yunjun, Jan 2017: using pysar._readfile/_writefile/_datetime
# Yunjun, Nov 2017: add support for geocoded file using input range distance


import os
import sys
import argparse
import time
import datetime

import h5py
import numpy as np

import pysar._datetime as ptime
import pysar._readfile as readfile
import pysar._writefile as writefile
import pysar._pysar_utilities as ut
from pysar._readfile import multi_group_hdf5_file, multi_dataset_hdf5_file, single_dataset_hdf5_file


#########################################################################################
def correct_lod_file(File, rangeDistFile=None, outFile=None):
    # Check Sensor Type
    print 'correct Local Oscilator Drift for Envisat using an empirical model (Marinkovic and Larsen, 2013)'
    print 'input file: '+File
    atr = readfile.read_attribute(File)
    k = atr['FILE_TYPE']
    platform = atr['PLATFORM']
    print 'platform: '+platform
    if not platform.lower() in ['env','envisat']:
        print 'No need to correct LOD for '+platform
        sys.exit(1)

    # Output Filename
    if not outFile:
        ext = os.path.splitext(File)[1]
        outFile = os.path.splitext(File)[0]+'_LODcor'+ext

    # Get LOD phase ramp from empirical model
    if not rangeDistFile:
        print 'calculate range distance from input file attributes'
        width = int(atr['WIDTH'])
        length = int(atr['FILE_LENGTH'])
        range_resolution = float(atr['RANGE_PIXEL_SIZE'])
        rangeDist1D = range_resolution * np.linspace(0, width-1, width)
        rangeDist = np.tile(rangeDist1D, (length, 1))
    else:
        print 'read range distance from file: %s' % (rangeDistFile)
        rangeDist = readfile.read(rangeDistFile, epoch='slantRangeDistance')[0]

    yref = int(atr['ref_y'])
    xref = int(atr['ref_x'])
    rangeDist -= rangeDist[yref][xref]
    Ramp = np.array(rangeDist * 3.87e-7, np.float32)

    # Correct LOD Ramp for Input File
    if k in multi_group_hdf5_file+multi_dataset_hdf5_file:
        h5 = h5py.File(File,'r')
        epochList = sorted(h5[k].keys())
        epochNum = len(epochList)

        print 'writing >>> %s' % (outFile)
        h5out = h5py.File(outFile,'w')
        group = h5out.create_group(k)

        prog_bar = ptime.progress_bar(maxValue=epochNum)
        if k in ['interferograms','wrapped']:
            Ramp *= -4*np.pi / float(atr['WAVELENGTH'])
            print 'number of interferograms: '+str(epochNum)
            date12List = ptime.list_ifgram2date12(epochList)
            for i in range(epochNum):
                epoch = epochList[i]
                data = h5[k][epoch].get(epoch)[:]
                atr = h5[k][epoch].attrs
                
                dates = ptime.yyyymmdd(atr['DATE12'].split('-'))
                dates = ptime.yyyymmdd2years(dates)
                dt = dates[1] - dates[0]
                data -= Ramp*dt

                gg = group.create_group(epoch)
                dset = gg.create_dataset(epoch, data=data, compression='gzip')
                for key, value in atr.iteritems():
                    gg.attrs[key] = value
                prog_bar.update(i+1, suffix=date12List[i])

        elif k == 'timeseries':
            print 'number of acquisitions: '+str(len(epochList))
            tbase = [float(dy)/365.25 for dy in ptime.date_list2tbase(epochList)[0]]
            for i in range(epochNum):
                epoch = epochList[i]
                data = h5[k].get(epoch)[:]

                data -= Ramp*tbase[i]

                dset = group.create_dataset(epoch, data=data, compression='gzip')
                prog_bar.update(i+1, suffix=epoch)
            for key, value in atr.iteritems():
                group.attrs[key] = value
        else:
            print 'No need to correct for LOD for '+k+' file'
            sys.exit(1)
        prog_bar.close()
        h5.close()
        h5out.close()

    elif k in ['.unw']:
        data, atr = readfile.read(File)
        Ramp *= -4*np.pi / float(atr['WAVELENGTH'])
        dates = ptime.yyyymmdd(atr['DATE12'].split('-'))
        dates = ptime.yyyymmdd2years(dates)
        dt = dates[1] - dates[0]
        data -= Ramp * dt
        print 'writing >>> %s' % (outFile)
        writefile.write(data, atr, outFile)
    else:
        print 'No need to correct for LOD for %s file' % (k)

    return outFile


#########################################################################################
REFERENCE='''reference:
  Marinkovic, P., and Y. Larsen (2013), Consequences of long-term ASAR local oscillator 
  frequency decay - An empirical study of 10 years of data, in Living Planet Symposium,
  Edinburgh, U.K.
'''

EXAMPLE='''example:
  lod.py timeseries.h5
  lod.py unwrapIfgram.h5  -r geometryGeo.h5
  lod.py filt_101020_110220_4rlks.unw
'''

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Local Oscilator Drift correction of Envisat',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=REFERENCE+'\n'+EXAMPLE)

    parser.add_argument(dest='file', help='timeseries / interferograms file, i.e. timeseries.h5')
    parser.add_argument('-r','--range', dest='range_dist_file',\
                        help='Slant range distance file, i.e. rangeDistance.h5, geometryGeo.h5')
    parser.add_argument('-o','--output', dest='outfile',\
                        help='Output file name for corrected file.')

    inps = parser.parse_args()
    return inps


#########################################################################################
def main(argv):
    inps = cmdLineParse()
    if not inps.outfile:
        inps.outfile = os.path.splitext(inps.file)[0]+'_LODcor'+os.path.splitext(inps.file)[1]

    atr = readfile.read_attribute(inps.file)
    if 'Y_FIRST' in atr.keys():
        coordType = 'geo'
    else:
        coordType = 'radar'
    print 'Input file is in %s coordinates' % (coordType)
    inps.range_dist_file = ut.get_geometry_file('slantRangeDistance', coordType=coordType)
    inps.outfile = correct_lod_file(inps.file, inps.range_dist_file, inps.outfile)
    print 'Done.'


#########################################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
