import glob
import json
import os
from pprint import pprint

import Options


def main():
    args = Options.get_args()
    row = args.row
    column = args.col

    # row =
    # column = 2

    path = '../log/'
    infiles = sorted(glob.glob(os.path.join(path, '*.json')), key=os.path.getmtime)

    res = []
    for infile in infiles:
        # find
        with open(infile) as f:
            data = json.load(f)
            for key,value in data.items():
                if key == str((row, column)):
                    res.append(value)

    output = f'result/{args.prov}'
    with open(output, 'w')as file:
        file.write(str(res))
    return res


if __name__ == '__main__':
    main()