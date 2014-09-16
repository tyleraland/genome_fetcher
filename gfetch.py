#!/usr/bin/env python

import sys
import argparse
import pandas
import ftputil
import os

url = 'ftp.ncbi.nih.gov'

# Note: NCBI has discontinued strain-level typing using TaxIDs.
# For more info, see http://www.ncbi.nlm.nih.gov/news/11-21-2013-strain-id-changes/

def get_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', help="'search' or 'fetch'")
    parser.add_argument('-n', '--name', nargs=2,
                        help="Scientific name, separated by spaces, case insensitive.\
                              Name must exist somewhere in organism's listed name")
    parser.add_argument('-s', '--status', default="complete gapless_chromosome chromosome",
                        help="Types of genomes to consider, separated by spaces, case insensitive.\
                              Options: complete gapless_chromosome chromosome\
                                       chromosome_with_gaps scaffold contig\
                              Default: complete gapless_chromosome chromosome")
    parser.add_argument('-o', '--outdir', default='genomes',
                        help="Directory to downlaod genomes to")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Enable verbose search output")

    return parser.parse_args()

def main():
    args = get_args()
    if args.action not in ['search', 'fetch']:
        sys.stdout.write("Improper action '{}'.  See help".format(args.action))

    # Metadata file which we will use to filter results and ultimately download data
    manifest = '/genomes/GENOME_REPORTS/prokaryotes.txt'

    host = ftputil.FTPHost(url, 'anonymous')
    host.download(manifest, 'genomes.txt')
    manifest_file = open('genomes.txt','r')
    manifest_file.seek(10) # Remove the first few chars of the first column so it's named 'Name'
    meta = pandas.read_csv(manifest_file, header=0, sep='\t')

    if args.name:
        # If a name was given, only look at organisms containing that name
        name = ' '.join(args.name)
        name = name[0].upper() + name[1:].lower()
        meta = meta[meta['Name'].str.contains(name, case=False)]
    if args.status:
        # If list of statuses was given, only look at organisms containing one of those
        statuses = args.status.split(' ')
        statuses = ['(^' + status.replace('_', ' ') + '$)' for status in statuses]
        statuses = '|'.join(statuses)
        meta = meta[meta['Status'].str.contains(statuses, case=False) ]
    meta = meta[meta['FTP Path'] != '-'] # Drop entries with no data to download
    meta = meta.drop_duplicates('TaxID') # Occasionally this signals duplicate strains

    if args.action == 'search':
        if args.verbose:
            print(meta)
        else:
            print('|' +
                  '|\t|'.join(['Name', 'Group', 'Subgroup', 'Status']) +
                  '|')
            for i,row in meta.iterrows():
                print('|' + 
                      '|\t|'.join([row['Name'], row['Group'], row['SubGroup'], row['Status']]) +
                      '|')
    elif args.action == 'fetch':
        try:
            os.makedirs(args.outdir)
        except OSError:
            pass
        basedir = 'genomes/ASSEMBLY_BACTERIA'
        for i,row in meta.iterrows():
            chromosome = row['Chromosomes/RefSeq'][:-2] + '.fna'
            uri = os.path.join(basedir,  row['FTP Path'],  chromosome)
            host.download(uri, os.path.join(args.outdir, chromosome))

    host.close()

if __name__ == '__main__':
    sys.exit(main())
