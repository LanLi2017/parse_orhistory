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


def main():
    args = Options.get_args()
    row = args.row
    column = args.col
    # row = 2
    # column = 5

    path = f'../{args.log}/'
    # path ='../log2/'
    infiles = sorted(glob.glob(os.path.join(path, '*.json')), key=os.path.getmtime)

    res = []
    for infile in infiles:
        # find
        filep = os.path.splitext(infile)[0]
        filename = filep.split('/')[-1]
        with open(infile) as f:
            data = json.load(f)
            for key,value in data.items():
                if key == str((row, column)):
                    old_value = getvalue(value['old'])
                    olddict = {old_value: (row, column)}
                    new_value = getvalue(value['new'])
                    newdict = {new_value: (row, column)}
                    res.append((filename,olddict, newdict))

    output = f'result/{args.out}'
    with open(output, 'w')as file:
        file.write(str(res))
    return res


if __name__ == '__main__':
    main()