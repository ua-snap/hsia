#!/usr/bin/env python

import argparse, getpass
class Password(argparse.Action):
    ''' simple class to capture password input from argparse with getpass'''
    def __call__(self, parser, namespace, values, option_string):
        if values is None:
            values = getpass.getpass()

        setattr(namespace, self.dest, values)


if __name__ == '__main__':
    import os

    # parse some args
    parser = argparse.ArgumentParser( description='download data from NSIDC-0051 Monthly for a given year using NASA EarthData login credentials' )
    parser.add_argument( "-o", "--out_path", action='store', dest='out_path', type=str, help="output directory to dump out the downloaded data" )
    parser.add_argument( "-y", "--year", action='store', dest='year', type=int, help="year to download from the NSIDC-0051 Monthly data archive." )
    parser.add_argument( "-u", "--username", action='store', nargs='?', dest='username', help="NASA EarthData username" )
    parser.add_argument( "-p", "--password", action=Password, nargs='?', dest='password', help="NASA EarthData password" )
    
    # unpack args
    args = parser.parse_args()
    out_path = args.out_path
    year = args.year
    username = args.username
    password = args.password

    for month in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        print( month )
        commanda = 'wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies --no-check-certificate --auth-no-challenge=on -r --reject "index.html*" -np -e robots=off --user {} --password {} '.format( username, password )
        commandb = 'https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0051_gsfc_nasateam_seaice/final-gsfc/north/monthly/nt_{}{}_f17_v1.1_n.bin'.format( str(year),month )
        os.system( commanda+commandb )