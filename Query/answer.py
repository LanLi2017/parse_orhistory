import glob
import json
import os
from pprint import pprint

import Options


def getvalue(data:str):
    if isinstance(data, dict):
        return data['v']
    else:
        try:
            value = json.loads(data)
            return value['v']
        except TypeError:
            return None


# def return_dependency(data):
 #  ''' can not return then dependency ''''
 #
#     ''' return dependency of provenance '''
#     op = data['op']
    # "ColumnAdditionChange": "columnIndex": "2",
    #
    # pass


def return_history(datas, row, column):
    ''' return the history of single cell '''
    ''' return the dependency 
        :return provenance = dependency + history'''
    # his = []
    # deps = []
    his = []
    for d in datas:
        data = d[1]
        filename = d[0]
        for key,value in data.items():
            if key == str((row, column)):
                # pass data to return dependency
                # deps.append(return_dependency(data))
                # return history
                old_value = getvalue(value['old'])
                olddict = {old_value: (row, column)}
                new_value = getvalue(value['new'])
                newdict = {new_value: (row, column)}
                his.append((filename,olddict, newdict))
    # prov = his + deps
    return his


# def return_prov(datas,row,column):
#     ''' return provenance by history + dependency '''
#     cell_history = return_history(datas, row, column)
#
#     pass


def main():
    args = Options.get_args()
    row = args.row
    column = args.col
    # row = 2
    # column = 5

    path = f'../{args.log}/'
    # path ='../log2/'
    infiles = sorted(glob.glob(os.path.join(path, '*.json')), key=os.path.getmtime)

    merge_data = []
    filenames = []
    for infile in infiles:
        # find
        filep = os.path.splitext(infile)[0]
        filename = filep.split('/')[-1]
        with open(infile) as f:
            data = json.load(f)
        filenames.append(filename)
        merge_data.append(data)
    datas = list(zip(filenames, merge_data))

    ''' provenance and history '''
    res = return_history(datas, row, column)

    output = f'result/{args.out}'
    with open(output, 'w')as file:
        file.write(str(res))
    return res


if __name__ == '__main__':
    main()