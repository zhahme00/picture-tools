import os
import sys
import argparse
import calendar
import shutil
import filecmp
import time
import glob

def args_parser():
    '''defines and returns the command line arguments for this script'''    
    ap = argparse.ArgumentParser(description = 'Organizes pictures from '
            'source folder to destination folder by copying (or moving) '
            'files into subfolders arranged by year & month.')
    # required parameters
    ap.add_argument('source', help='the folder (and subfolders inside it) '
            'that will be scanned for files that need to be arranged.')
    ap.add_argument('destination', 
            help='the folder where files will be organized (i.e., '
            'copied or moved to) inside subfolders arranged by year '
            'and month.')
    # the following are optional parameters
    ap.add_argument('-m', '--move', action='store_true',
            help='move the files from the source folder to the '
            'destination folder. The default operation is to copy '
            'files from the source to the destination folder, i.e., '
            'leaves the contents of the source folder intact.')
    ap.add_argument('-np', '--noprompt', action='store_true', 
            help='just do it, don\'t prompt for y/n') 
    # ap.add_argument('-s', '--startdate', type=valid_date,
            # help='process files starting from date') 
    return ap

def destination_subfolder(stat):
    '''Creates a subfolder using creation time and modified time.
       Sub folder is in the format:
         year\month number - abbr. month name\
         
       Example: 
         2014\4 - Apr\
         2015\1 - Jan\ '''
    file_time = time.localtime(min(stat.st_ctime, stat.st_mtime))
    subfolder = '%s\%s - %s\\' % (file_time.tm_year, 
                file_time.tm_mon, calendar.month_name[file_time.tm_mon][:3])
    return subfolder

def get_unique_filename(f):
    '''Creates a unique file name from the filename provided in 
       the parameter. 
       
       Unique name is created by appending numbers to the end of 
       the file name and checking via os calls for existance of 
       file with the same name.'''
    root, ext = os.path.splitext(f)
    for i in range(1, 100000):
        if not os.path.exists('%s (%s) %s' % (root, i, ext)):
            return '%s (%s) %s' % (root, i, ext)
    return None
    
def main():
    '''Organizes pictures by year and month by copying from 
       source to destination folder.'''
    args = args_parser().parse_args()
    dest_root_folder = os.path.abspath(args.destination) + os.sep
    source_folder = os.path.abspath(args.source) + os.sep
    # validate source and destination folders
    if source_folder == dest_root_folder:
        print('Source and destination folders cannot be the same!')
        sys.exit(4)
    for folder in [source_folder, dest_root_folder]:
        if not os.path.exists(folder):
            print('Folder \'%s\' is invalid or does not exists!' % folder)
            sys.exit(4)
            
    prompt = not args.noprompt
    skipped, operated = 0, 0
    skipped_folders = []
    dest = None
    
    # final prompt before damage
    if prompt and input("Copying files from '%s' to '%s'. Proceed [y|n]? " %
                        (source_folder, dest_root_folder)) == 'n':
        sys.exit(0)
    
    print('Scanning folder \'%s\'\n' % source_folder)
    source_files = ((f, os.stat(f)) 
                    for f in glob.iglob(source_folder + '**/*', recursive=True) 
                    if os.path.isfile(f))
    for src, stat in source_files:
        dest_folder = dest_root_folder + destination_subfolder(stat)
        if dest_folder in skipped_folders:
            print('Skipping file \'%s\'' % src)
            skipped += 1
            continue
        if not os.path.exists(dest_folder):
            # the destination folder doesn't exist (so the file 
            # doesn't exist either). Create the destination or
            # skip creating it and hence skip the file.
            #
            # no prompt (or silent run) means we create destination folders
            if prompt:
                if input('Create folder \'%s\' [y|n]? ' % dest_folder) == 'n':
                    print('Skipping file \'%s\'' % src)
                    skipped_folders.append(dest_folder)
                    skipped += 1
                    continue
            print('Creating destination folder %s' % dest_folder)
            # todo: 
            os.makedirs(dest_folder)
            dest = dest_folder + os.path.basename(src)
        else:
            # the destination directory exists; does the file?
            dest = dest_folder + os.path.basename(src)
            if os.path.exists(dest):
                # compare for equality 
                if filecmp.cmp(src, dest, shallow=False):
                    print('Skipping file \'%s\' as duplicate exists '
                          'at \'%s\'' % (src, dest))
                    skipped += 1
                    continue
                else:
                    print('File name already exists; generating new name!')
                    dest = get_unique_filename(dest)
        print('Copying %s to %s' % (src, dest))
        # todo: 
        shutil.copy2(src, dest)
        operated += 1
    print('%s file(s) total; %s copied; %s skipped' % 
          (operated + skipped, operated, skipped))
    
if __name__ == '__main__':
    main()