#!/usr/bin/env python

import sys
import argparse
import pandas
import ftputil
import os

url = 'ftp.ncbi.nih.gov'

def get_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', help="'search' or 'fetch'")
    parser.add_argument('-n', '--name', nargs=2,
                        help='Scientific name, separated by spaces, not case sensitive')
    parser.add_argument('-s', '--status', default="complete gapless_chromosome chromosome",
                        help="Options: complete, gapless_chromosome, chromosome, chromosome_with_gaps, scaffold, contig")
    parser.add_argument('-o', '--outdir', default='genomes',
                        help="Directory to downlaod genomes to")

    return parser.parse_args()

def main():
    args = get_args()
    if args.action not in ['search', 'fetch']:
        sys.stdout.write("Improper action '{}'.  See help".format(args.action))

    manifest = '/genomes/GENOME_REPORTS/prokaryotes.txt'

    #ftp.login()                     # Login is anonymous, otherwise 'sftp' package is preferred
    host = ftputil.FTPHost(url, 'anonymous')
    host.download(manifest, 'genomes.txt')
    manifest_file = open('genomes.txt','r')
    manifest_file.seek(10) # Remove the first few chars of the first column so it's named 'Name'
    meta = pandas.read_csv(manifest_file, header=0, sep='\t')

    if args.name:
        name = ' '.join(args.name)
        name = name[0].upper() + name[1:].lower()
        meta = meta[meta['Name'].str.contains(name, case=False)]
    if args.status: # [complete, gapless_chromosome, ...]
        statuses = args.status.split(' ')
        statuses = ['(' + status.replace('_', ' ') + ')' for status in statuses]
        statuses = '|'.join(statuses)
        statuses = '^' + statuses + '$'
        meta = meta[meta['Status'].str.contains(status, case=False) ]
    meta = meta[meta['FTP Path'] != '-'] # Drop entries with no data to download
    meta = meta.drop_duplicates('TaxID') # Occasionally this signals duplicate strains

    if args.action == 'search':
        for i,row in meta.iterrows():
            print(row['Name'])

    try:
        os.makedirs(args.outdir)
    except OSError:
        pass
    basedir = 'genomes/ASSEMBLY_BACTERIA'
    for i,row in meta.iterrows():
        chromosome = row['Chromosomes/RefSeq'][:-2] + '.fna'
        uri = os.path.join(basedir,  row['FTP Path'],  chromosome)
        #ftp.retrbinary('RETR {}'.format(uri), open(os.path.join(args.outdir, chromosome),'w').write)
        host.download(uri, os.path.join(args.outdir, chromosome))
        break
#        print(row['FTP Path'])

#    dirnames = ftp.nlst()          # Returns directory contents
    
#    for dirname in dirnames:
#        if target.lower().replace(' ','_') in dirname.lower():
#            ftp.cwd(dirname)
#        if 'Staphylococcus
#        
#    print("staph aureus: {}".format(len([dirname for dirname in filenames if 'staphylococcus_aureus' in dirname.lower() ])))

    host.close()

if __name__ == '__main__':
    sys.exit(main())
