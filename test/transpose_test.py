import json
import re
from pprint import pprint
import numpy as np


def compare_list(old:list, new:list, row:int, op:dict):
    # index initialization
    y = 0
    edits = dict()
    olddict = dict()
    newdict = dict()
    for x in old:
        if x != new[y] or x==new[y]=={'v':None}:
            # col_idx_list.append(y)
            x_y = (row, y)
            old_value = old[y]
            new_value = new[y]
            #   "old": "{\"v\":\" 2070\"}",
            olddict['old'] = old_value
            newdict['new'] = new_value
            edits[str(x_y)]=  {'row': row,
                                'cell': y,
                               }
            edits[str(x_y)].update(olddict)
            edits[str(x_y)].update(newdict)
            op.update(edits)
        y = y+1

    return op


def padding_data(data, num_rows, num_cols):
    row = len(data)
    column = len(data[0])
    pad_row = abs(num_rows-row)
    pad_col = abs(num_cols-column)

    for d in data:
        # ['laura@example.com' ' 2070' ' Laura' ' Grey']
        if pad_col != 0:
           d.extend([{"v": None}]*pad_col)
        elif pad_col == 0:
            pass
    if pad_row == 0:
        pass
    elif pad_row != 0:
        for i in range(pad_row):
            data.append([{"v": None}]*num_cols)
    return data


# def extract_value(v:dict):
#     if v:
#         return v['v']
#     else:
#         return None


def transpose_cols_rows(topping:list, content:list):
    ''' transpose : topping: 1'''
    opname = topping[0].split('.')[-1]
    op = {'op': opname}

    idx = 0
    new_col_count = 0
    old_col_count = 0
    new_row_count = 0
    old_row_count = 0

    # last half for new dataset, old dataset
    new_cells = []
    old_cells = []
    while idx < len(content):
        line = content[idx]
        if re.match(r'^newColumnCount=\d+',line):
            new_col_count = int(line.rsplit('=', 1)[1])
            new_col= content[idx+1:idx+1+new_col_count]
            op.update({'newColumnCount': new_col_count})
            # possible breakout:
            op.update({'newColumnModel': new_col})
            idx += new_col_count
        elif re.match(r'^oldColumnCount=\d+$', line):
            old_col_count = int(line.rsplit('=', 1)[1])
            op.update({'oldColumnCount': old_col_count})
            old_col = content[idx+1: idx+1+old_col_count]
            op.update({'oldColumnModel': old_col})
            idx += old_col_count
        elif re.match(r'^newRowCount=\d+$', line): # tuplecount idx = 0
            new_row_count = int(line.rsplit('=', 1)[1])
            op.update({'newRowCount': new_row_count})
            new_data = content[idx+1: idx+1+new_row_count]
            for value in new_data:
                # v_cells = []
                cells = json.loads(value)['cells']
                if len(cells) < new_col_count:
                    cells.extend([None] * (new_col_count - len(cells)))
                # for v in cells:
                #     v_cells.append(extract_value(v))

                new_cells.append(cells)
            idx += new_row_count

        elif re.match(r'^oldRowCount=\d+$', line):
            # need to remove the padding
            old_row_count = int(line.rsplit('=', 1)[1])
            op.update({'newRowCount': old_row_count})
            old_data = content[idx + 1: idx + 1 + old_row_count]
            for value in old_data:
                cells = json.loads(value)['cells'][:old_col_count]
                # v_cells = []
                # for v in cells:
                #     v_cells.append(extract_value(v))

                old_cells.append(cells)
            idx += old_row_count

        idx += 1

    # paddding old and new both
    num_rows = max(new_row_count, old_row_count)
    num_cols = max(new_col_count, old_col_count)
    # padding shape: num_rows * num_cols
    pad_new = padding_data(new_cells, num_rows, num_cols)
    print(pad_new)
    print('old: ===============')
    pad_old = padding_data(old_cells, num_rows, num_cols)
    print(pad_old)
    pairs = list(zip(pad_old, pad_new))
    for row in range(num_rows):
        pair = list(pairs[row])
        d1, d2 = pair
        compare_list(d1, d2, row, op)
    return op


def main():
    filepath = f'change.txt'
    # filepath = f'research_data/data2/history/1591944670566.change/transpose_chan.txt'
    # filepath = 'research_data/TAPP_data/changes/1591864798279.change/transpose_chan.txt'
    with open(filepath, 'r')as f:
        # txt = f.read()
        data = f.readlines()

    # data = txt.split('\n/ec/\n')
    data = [x.strip() for x in data]
    # different text file has different number of topping

    # top_count = args.num_top ; initialize
    top_count = 1
    head, top, content = data[0], data[1:top_count + 1], data[top_count + 1:]
    op = transpose_cols_rows(top, content)
    pprint(op)


if __name__ == '__main__':
    main()