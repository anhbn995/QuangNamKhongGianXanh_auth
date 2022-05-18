import os, glob


def get_name_file_from_dir(dir_fp, type_file='tif'):
    list_name = []
    len_type_name = 0 - (len(type_file) + 1)
    if glob.glob(os.path.join(dir_fp,f'*.{type_file}')):
        for fp in glob.glob(os.path.join(dir_fp,f'*.{type_file}')):
            file = os.path.basename(fp)
            list_name.append(file[:len_type_name])
        return list_name
    else:
        print(f'Khong ton tai file .{type_file} trong folder duoi: \n{dir_fp}')
        return False