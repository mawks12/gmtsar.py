#! /usr/bin/env python3
"""
proj_ra2ll is part of GMTSAR. 
This Python script is migrated from proj_ra2ll.csh by Dunyu Liu on 20231109.
proj_ra2ll.csh was originally written by David Sandwell on 20070112. 

Purpose: to project a grd file from range/azimuth coordinates into lon/lat coordinates.
  It takes in 
      - trans.dat, a file generated by llt_grid2rat (r, a, topo, lon, lat)
      - phase_ra.grd, a GRD file of phase or anything
  and output 
      - phase_ll.grd, a GRD file of phase in longtitude/latitude coordinates
"""

import sys
import subprocess
import glob
from gmtsar_lib import *


def proj_ra2ll():
    """
    Usage: proj_ra2ll trans.dat phase.grd phase_ll.grd [filter_wavelength]

    trans.dat    - file generated by llt_grid2rat  (r a topo lon lat)
    phase_ra.grd - a GRD file of phase or anything
    phase_ll.grd - output file in lon/lat-coordinates
    filter_wavelength - will sample every 1/4 wavelength (in meters)
    """

    print('PROJ_RA2ll - START ... ...')
    n = len(sys.argv)
    print('PROJ_RA2ll: input arguments are ', sys.argv)

    if n != 4 and n != 5:
        print('FILTER: Wrong # of input arguments; # should be 3 or 4 ... ...')
        print(proj_ra2ll.__doc__)

    V = '-V'

    print(' ')
    print('PROJ_RA2ll: extract the phase in the r a positions ... ...')
    run('gmt grd2xyz '+sys.argv[2]+' -s -bo3f > rap')

    print(' ')
    print('PROJ_RA2ll: make grids of longitude and latitude versus range and azimuth unless they already exist ... ...')

    if check_file_report('raln.grd') is False or check_file_report('ralt.grd') is False:
        # region = subprocess.check_output(["gmt","gmtinfo","rap","-I16/32","-bi3f"], universal_newlines=True)
        region = catch_output_cmd(
            ["gmt", "gmtinfo", "rap", "-I16/32", "-bi3f"], False, 0, -10000)
        print('PROJ_RA2ll: region is ', region)

        cmd = 'gmt surface ' + \
            sys.argv[1]+' -i0,1,3 -bi5d '+region+' -I16/32 -T.50 -Graln.grd '+V
        run(cmd)
        cmd = 'gmt surface ' + \
            sys.argv[1]+' -i0,1,4 -bi5d '+region+' -I16/32 -T.50 -Gralt.grd '+V
        run(cmd)

    print(' ')
    print('PROJ_RA2ll: add lon and lat columns and then just keep lon, lat, phase ... ...')

    run('gmt grdtrack rap -nl -bi3f -bo5f -Graln.grd -Gralt.grd | gmt gmtconvert -bi5f -bo3f -o3,4,2 > llp')

    print('PROJ_RA2ll: set the output grid spaccing to be 1/4 the filter wavelength ... ...')

    if n == 5:
        filt_wave = float(sys.argv[4])
        pix_m = filt_wave/4
        print('PROJ_RA2ll: Sampling in geocoordinates with ' +
              str(pix_m)+' meter pixels ... ...')
    else:
        filt = glob.glob("gauss_*")
        if filt:
            res = filt[0][6:]  # extract resolution from gauss_* string.
            pix_m = float(res)/4
            # use 1/4 wavelength
            print('PROJ_RA2ll: Sampling in geocoordinates with ' +
                  str(pix_m)+' meter pixels ...')
        else:
            pix_m = 60
            print('PROJ_RA2ll: Sampling in geocoordinates with deault (' +
                  str(pix_m)+' meter) pixel size ... ...')

    incs = subprocess.run(["m2s.csh", str(
        pix_m), "llp"], stdout=subprocess.PIPE).stdout.decode('utf-8').strip().split()
    print('PROJ_RA2ll: incs is ', incs)
    R = subprocess.run(["gmt", "gmtinfo", "llp", "-I"+incs[1], "-bi3f"],
                       stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    print('PROJ_RA2ll: R is ', R)

    cmd = 'gmt blockmedian llp '+R+' -bi3f -bo3f -I'+incs[0]+" -r -V > llpb"
    run(cmd)
    cmd = 'gmt xyz2grd llpb '+R+' -I' + \
        incs[0]+'  -r -fg -G'+sys.argv[3]+' -bi3f'
    run(cmd)
    run('rm rap* llp llpb raln ralt')

    print("PROJ_RA2ll - END ... ...")


def _main_func(description):
    proj_ra2ll()


if __name__ == "__main__":
    _main_func(__doc__)
