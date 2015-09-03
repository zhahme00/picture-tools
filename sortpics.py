import os
import argparse
import shutil
import calendar
import sys
import filecmp
from os import path
from os.path import abspath
from time import localtime
from pathlib import Path, PurePath
 
def args_parser():
    '''defines and returns the command line arguments for this script'''
    ap = argparse.ArgumentParser(description = 'Organizes pictures from '
            'source folder to destination folder by moving (or copying) '
            'files into subfolders arranged by year & month.')
    ap.add_argument('source', help='the folder to move files from')                             
    ap.add_argument('destination', help='the folder where files will be '
            'organized by year and month')
    ap.add_argument('-c', '--copy', help='just copy the files instead '
            'of moving them from the source', action='store_true')
    ap.add_argument('-s', '--silent', help='do not print progress or '
            'activity; prompts will NOT be suppressed however', 
            action='store_true')
    ap.add_argument('-np', '--noprompt', action='store_true', 
            help='just do it, don\'t prompt for y/n')
    return ap
    
def get_new_name(p: PurePath):
    '''returns a new file name by appending (1) to the existing
    file name. process is applied repeatedly until the file name 
    is unique'''
    p = p.parent.joinpath(p.stem + ' (1) ' + p.suffix)
    while path.exists(str(p)):
        p = p.parent.joinpath(p.stem + ' (1) ' + p.suffix)
    return p

def transform(s: PurePath, d: PurePath):
    '''moves or copies source (s) to destination (d). return 2-tuple
    containing (1, 0) or (0, 1) if copied or skipped respectively'''
    if not path.exists(str(d.parent)):
        # need to create this folder
        print('Creating folder %s' % d.parent)
        os.makedirs(str(d.parent))
    else:
        # name exists? compare for duplicate and skip if it is. 
        # otherwise, get a new name for the file
        if path.exists(str(d)):
            # compare for equality 
            if filecmp.cmp(str(s), str(d), shallow=False):
                print('Skipping duplicate file \'%s\'' % d)
                # 0 copied, 1 skipped
                return (0, 1)
            else:
                d = get_new_name(d)
                print('File name already exists; generating new name!')
    print('Copying %s to %s' % (s, d))
    shutil.copy2(str(s), str(d))
    # 1 copied, 0 skipped
    return (1, 0)
        
def main():
    '''move or copy all files from source to destination'''
    args = args_parser().parse_args()
    # TODO: support optional arguments.
    
    # validate passed in source and destination folders
    s_folder = abspath(args.source)
    d_folder = abspath(args.destination)
    for folder in [s_folder, d_folder]:
        if not path.isdir(folder):
            print('Folder \'%s\' is invalid or does not exists!' % folder)
            sys.exit(4)
    if s_folder == d_folder:
        print('Source and destination folders cannot be the same!')
        sys.exit(4)
 
    # iterate over all files
    skipped, copied = (0, 0)
    name_stat_pairs = ((str(p), p.stat()) 
                       for p in Path(s_folder).glob('**/*') if p.is_file())
    # min of modified and creation time is used because the act of 
    # copying files to a new folder will change the file creation 
    # time. the modified time seems to not get affected, however.
    name_time_pairs = ((PurePath(abspath(f)), localtime(min(s.st_ctime, s.st_mtime)))
                       for f, s in name_stat_pairs)
    for s_file, file_time in name_time_pairs:
        # the creation time is used to build the final destination of the file
        d_subfolder = '%s\%s - %s\\' % (file_time.tm_year, file_time.tm_mon, 
                 calendar.month_name[file_time.tm_mon][:3])
        d_file = PurePath(d_folder).joinpath(
                d_subfolder, s_file.name)
        c, s = transform(s_file, d_file)
        copied += c
        skipped += s
    print('%s file(s) total; %s copied; %s skipped' % 
            (copied + skipped, copied, skipped))
    
if __name__ == '__main__':
    main()