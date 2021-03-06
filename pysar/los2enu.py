#! /usr/bin/env python2
############################################################
# Program is part of PySAR v1.0                            #
# Copyright(c) 2013, Heresh Fattahi                        #
# Author:  Heresh Fattahi                                  #
############################################################

import sys
import os 
from  numpy import shape,pi,cos, sin
import getopt
import h5py 


def usage():
    print ''' 
**************************************************************************
  Projecting LOS (Line of Sight) InSAR measurements to different components
    
  Usage:
      los2enu.py -f  LOS file  -c Components [ -i incidence angle file] 
                 [-F 'fault coordinates'] [-a azimuth] [-H heading]
      
      -c : [E, N, U, H, Fpar]
      E : Projecting LOS to E (East), assuming zero North and Up components
      N : Projecting LOS to N (North), assuming zero East and Up components
      U : Projecting LOS to U (Up), assuming zero East and North components
      H : Projecting LOS to H (Horizontal), assuming zero Up component
      Fpar : Projecting LOS to Fault Parallel , assuming zero Up component 
             (This needs the azimuth of the fault or the  coordinates of two points on the fault )
      
      azimuth: azimuth angle of the fault from North (Clockwise in degrees)
      heading: heading angle of the satellite orbit from north (Clockwise in degrees)
 
   Example:

***************************************************************
    '''

############################################################################
def main(argv):
    try:  opts, args = getopt.getopt(argv,"f:h:c:i:F:I:a:H:")
    except getopt.GetoptError:  usage(); sys.exit(1)

    if opts==[]:    usage() ; sys.exit(1)
    for opt,arg in opts:
        if opt in ("-h","--help"):  usage();  sys.exit()
        elif opt == '-f':       File          = arg
        elif opt == '-c':       component     = arg
        elif opt == '-i':       incidenceFile = arg
        elif opt == '-I':       proj_inc      = float(arg)
        elif opt == '-a':       azimuth       = float(arg)
        elif opt == '-H':       heading       = float(arg)
  
    h5file=h5py.File(File,'r')
    k=h5file.keys()  
    Vset=h5file[k[0]].get(k[0])
    V=Vset[0:Vset.shape[0],0:Vset.shape[1]]

    try:
        h5incidence=h5py.File(incidenceFile,'r')
        iset=h5incidence['mask'].get('mask')
        inc=iset[0:iset.shape[0],0:iset.shape[1]]
    except:
        print 'Incidence angle was not found or is not readable!'
        print 'Continue with average look angle'
        look_n=float(h5file[k[0]].attrs['LOOK_REF1'])
        look_f=float(h5file[k[0]].attrs['LOOK_REF2']) 
        inc=(look_n+look_f)/2.
        inc=41.0
        print 'Average look angle = '+str(inc)
  
    inc=inc*pi/180.
   
    if component in 'U, u, Up, up, uP':
        P = V/cos(inc) # projecting LOS to up assuming zero horizontal deformation
        outName='up.h5'
    
    elif component in 'H , h, horizontal, Horizontal':
        P = V/sin(inc) # projecting LOS to up assuming zero horizontal deformation
        outName='Horizontal.h5'
  
    elif component=='Fpar':
       # az=28.31*pi/180.
       # h=346.8921*pi/180.
        try:
            az=azimuth*pi/180.
        except:
            print ''         
            print 'Error: azimuth of the fault is required!';
            print ''
            sys.exit(1)
  
        try:
            h=heading*pi/180.
        except:
            print 'trying to use the heading angle from '+File 
            heading = float(h5file[k[0]].attrs['HEADING'])
            if heading < 0:
                heading=heading+360
            h=heading*pi/180.
        
        print '******************************************'  
        print 'Fault Azimuth = '+str(azimuth)
        print 'Satellite Heading Angle = '+str(heading)
        print '******************************************'
  
        fac=sin(az)*cos(h)*sin(inc)-cos(az)*sin(h)*sin(inc)
        P = V/fac 
        
        
        outName='Fault_parallel.h5'
  
    elif component=='los':
        try:
            proj_inc=proj_inc*pi/180.       
        except:
            print 'Error: los option projects the current los to a different los with \
            a given inc angle. It needs the new inc angle to be introdueced using -I option'
            sys.exit(1)
        inc=inc-proj_inc
        P = V*cos(inc) # projecting LOS to up assuming zero horizontal deformation
        outName='projected_los.h5'
  
    print 'writing '+outName    
    h5file2 = h5py.File(outName,'w')
    group=h5file2.create_group(k[0])
    dset = group.create_dataset(k[0], data=P, compression='gzip')
    
    for key, value in h5file[k[0]].attrs.iteritems():
            group.attrs[key] = value
      
    h5file.close()
    h5file2.close()


############################################################################
if __name__ == '__main__':
    main(sys.argv[1:])



