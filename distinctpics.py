import os
import filecmp
from pathlib import Path
from argparse import ArgumentParser

logging_enabled = True

def log(msg):
    if logging_enabled:
        print(msg)

def get_parser() -> ArgumentParser:
    ap = ArgumentParser(
            description='Removes duplicate (picture) files from a folder.')
    ap.add_argument('folder', help='The folder (and subfolders inside) that '
            'is to be scanned for duplicate files. Use a \'.\' (without the '
            'quotes if the current folder is to be scanned.')
    ap.add_argument('-q', '--quiet', help='do not print progress or '
            'activity', action='store_true')
    ap.add_argument('-dry', '--dryrun', help='perform a simulation without '
            'erasing any duplicates', action='store_true')
    # todo: list duplicates
    return ap

def group_by_size(folder: str):
    '''Returns a dictionary of all files in the folder 
    (and subfolders), grouped by file size'''
    sizes = {}
    for f, s in ((p, p.stat().st_size) 
                 for p in Path(folder).glob('**/*') if p.is_file()):
        if s in sizes:
            sizes[s].append(f)
        else:
            sizes[s] = [f]
    return sizes
    
def group_byte_equals(files):
    '''From the files parameter, groups into lists files that are byte equal. 
    For example: Calling group_byte_equals([A, B, C, D, E, F] will yeild
    2 lists [A, C, D] and [B, F] if files A = C = D,  B = F, and file E is
    has the same size as all the others but is not byte equal to any.'''
    # Copy to eliminate side effects
    files = list(files)
    print(files)
    i = 0
    while i < len(files):
        duplicates = [files[i]]
        j = i + 1
        while j < len(files):
            print(files[i], files[j])
            if filecmp.cmp(str(files[i]), str(files[j]), shallow = False):
                duplicates.append(files.pop(j))
            else:
                j += 1
        # The base file compared against should be 
        # returned too if duplicates were found.
        if len(duplicates) > 1:
            yield duplicates
        i += 1

def main():
    args = get_parser().parse_args()
    logging_enabled = not args.quiet
    folder = os.path.abspath(args.folder)
    grouped_files = group_by_size(folder)
    # if a size group has only 1 item then it has no duplicates!
    candidate_duplicates = ((size, file_list) 
                            for (size, file_list) in grouped_files.items()
                            if len(file_list) > 1)
    same_sizes = (pair[1] for pair in candidate_duplicates)
    byte_equals = (group_byte_equals(s) for s in same_sizes)
    for b in byte_equals:
        for x in b:
            print(x)
        print('\n')
    pass
    
if __name__ == '__main__':
    main()