'''
op: ; % operation name /according to result
row: ; % row indices
cell: ; % column indices
edits :[
{
old:,
new:,
}
]
# DTA
{
(old -> (row, cell), new -> (row, cell))
()
}
 (row, cell) : {}

'''
from pprint import pprint
import Options
import re
import json


def list_split_cond(items, sep_cond, maxsplit=-1):
    """
    split list into sublist by condition

    >>> list_split_cond([1,2,3,4,5], lambda  x: x==3)
    [[1,2], [4,5]]
    >>> list_split_cond([1,1,1], lambda  x: x==1)
    [[], [], [], []]
    >>> list_split_cond('apple', 'p'.__eq__)
    [['a'], [], ['l','e']]
    """
    items = list(items)
    if maxsplit == 0:
        return [items]
    split_idx = []
    for idx, item in enumerate(items):
        if sep_cond(item):
            split_idx.append(idx)
            if 0 < maxsplit <= len(split_idx):
                break
    return [
        items[start +1:end] # split : 1,5,8
        for start, end in zip(
            [-1, *split_idx], # -1， 1， 5， 8
            [*split_idx, len(items)] # 1， 5， 8， 9
        ) # [(-1,1), (1,5), (5,8), (8,9)] -> ITEMS [0,1] [2,5] [6,8] [9,9]
    ]


def Common_transform(topping:list,content:list):
    ''' common transformation: topping: 4'''
    # content: list
    # operation name
    opname = topping[0].split('.')[-1]
    op = {'op':opname}
    res = dict(item.split("=") for item in topping[1:])
    op.update(res)

    # deal with content
    Content = list_split_cond(content, '/ec/'.__eq__)
    # remove empty
    TContent = [x for x in Content if x]

    # Content = [value.remove('/ec/') for value in content]
    content_dict = dict()
    for value in TContent:
        res = dict(item.split("=") for item in value)
        row_idx = res['row']
        cell_idx = res['cell']
        idx = (row_idx, cell_idx)
        res_dict = {str(idx): res}
        content_dict.update(res_dict)
    op.update(content_dict)
    return op


def col_addition(topping:list, content:list):
    ''' column addition : topping 5'''
    # column name / column index / [newCellIndex]/ newCellCount
    opname = topping[0].split('.')[-1]
    op = {'op': opname}
    res = dict(item.split("=") for item in topping[1:])
    op.update(res)
    cell = op['newCellIndex']

    # content
    Content = list_split_cond(content, '/ec/'.__eq__)
    # remove empty
    TContent = [x for x in Content if x]

    content_dict = dict()
    for value in TContent:
        for item in value:

            # new_item = re.split(';|=', item)
            if re.match('\d+;.*', item):
                new_item = item.split(';', maxsplit=1)
                row_idx = new_item[0]
                cell_value = new_item[1]
                cell_idx = cell
                idx = (row_idx, cell_idx)
                res_dict = {str(idx): cell_value}
                content_dict.update(res_dict)

            elif re.match('\w+=.*', item):
                new_item = item.split('=', maxsplit=1)
                key, value = new_item[0], new_item[1]
                content_dict.update({key: value})
    op.update(content_dict)
    return op


def col_remove(topping:list, content:list):
    ''' rename column topping: 3'''
    opname = topping[0].split('.')[-1]
    op = {'op': opname}

    # input data status ; view index -> physical idx || saved index/actual index
    old_col = dict(item.split("=") for item in topping[1:])

    # oldColumnIndex = old_col['oldColumnIndex']
    oldColumn = json.loads(old_col['oldColumn'])
    cellIdx = oldColumn['cellIndex']

    op.update(old_col)

    # content
    Content = list_split_cond(content, '/ec/'.__eq__)
    # remove empty
    TContent = [x for x in Content if x]

    content_dict = dict()
    for value in TContent:
        for item in value:
            # new_item = re.split(';|=', item)
            if re.match('\d+;.*', item):
                new_item = item.split(';', maxsplit=1)
                row_idx = new_item[0]
                cell_value = new_item[1]
                # cell_idx = oldColumnIndex
                cell_idx = cellIdx
                idx = (row_idx, cell_idx)
                res_dict = {str(idx): cell_value}
                content_dict.update(res_dict)

            elif re.match('\w+=.*', item):
                new_item = item.split('=', maxsplit=1)
                key, value = new_item[0], new_item[1]
                content_dict.update({key: value})
    op.update(content_dict)
    return op


func_map ={
    'MassCellChange': Common_transform,
    'ColumnAdditionChange': col_addition,
    'ColumnRemovalChange': col_remove,

}


def main():

    args = Options.get_args()
    #
    filepath =f'research_data/TAPP_data/changes/{args.file_path}/change.txt'
    # filepath = 'research_data/TAPP_data/changes/1591317229023.change/change.txt'
    with open(filepath, 'r')as f:
        # txt = f.read()
          data = f.readlines()

        # data = txt.split('\n/ec/\n')
    data = [x.strip() for x in data]
    # different text file has different number of topping

    top_count = args.num_top
    # top_count = 3
    head, top, content = data[0], data[1:top_count+1], data[top_count+1:]

    # mapping to different function
    opname = top[0].split('.')[-1]

    # common transformation : upper/lower/...
    prov_path = f'log/{args.log}'
    # prov_path = 'log/prov6.json'
    op = [func_map[opname](top, content)]
    pprint(op)
    with open(prov_path, "w") as outfile:
        json.dump(op, outfile, indent=4)


if __name__ == '__main__':
    main()