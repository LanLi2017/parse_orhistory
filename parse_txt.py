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
import os


def compare_list(old:list, new:list, row:int, op:dict):
    # index initialization
    y = 0
    edits = dict()
    # col_idx_list = []
    # x_y = tuple()
    # old_value = None
    # new_value = None
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


def pad_or_truncate(old:list, target_len:int):
    # adding more null
    new = old[:target_len] +[{"v": None}]*(target_len - len(old))
    return new


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


def padding_data(data, num_rows, num_cols):
    ''' padding old lists, new lists -> make them into the same shape'''
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
#     # extract value from transpose
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
        elif re.match(r'^newRowCount=\d+$', line):  # tuplecount idx = 0
            new_row_count = int(line.rsplit('=', 1)[1])
            op.update({'newRowCount': new_row_count})
            new_data = content[idx + 1: idx + 1 + new_row_count]
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
    pad_old = padding_data(old_cells, num_rows, num_cols)
    pairs = list(zip(pad_old, pad_new))
    for row in range(num_rows):
        pair = list(pairs[row])
        d1, d2 = pair
        compare_list(d1, d2, row, op)
    return op


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
        row_idx = int(res['row'])
        cell_idx = int(res['cell'])
        idx = (row_idx, cell_idx)
        res_dict = {str(idx): res}
        content_dict.update(res_dict)
        content_dict.update({'cellindex': cell_idx})
    op.update(content_dict)
    return op


def col_addition(topping:list, content:list):
    ''' column addition : topping 5'''
    # column name / column index / [newCellIndex]/ newCellCount
    opname = topping[0].split('.')[-1]
    op = {'op': opname}
    res = dict(item.split("=") for item in topping[1:])
    op.update(res)
    cell = int(op['newCellIndex'])

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
                row_idx = int(new_item[0])
                cell_value = new_item[1]
                cell_idx = cell
                idx = (row_idx, cell_idx)
                res_dict = {str(idx): cell_value}
                res_dict[str(idx)] = {
                    'old': None,
                    'new': res_dict[str(idx)],
                }
                content_dict.update(res_dict)

            elif re.match('\w+=.*', item):
                # oldColumnGroupCount=0
                new_item = item.split('=', maxsplit=1)
                key, value = new_item[0], new_item[1]
                content_dict.update({key: value})
    op.update({'cellindex': cell})
    op.update(content_dict)
    return op


def col_remove(topping:list, content:list):
    ''' remove column topping: 3'''
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
                row_idx = int(new_item[0])
                cell_value = new_item[1]
                # cell_idx = oldColumnIndex
                cell_idx = cellIdx
                idx = (row_idx, cell_idx)
                res_dict = {str(idx): cell_value}
                res_dict[str(idx)] = {
                    'old': res_dict[str(idx)],
                    'new': None,
                }
                content_dict.update(res_dict)

            elif re.match('\w+=.*', item):
                new_item = item.split('=', maxsplit=1)
                key, value = new_item[0], new_item[1]
                content_dict.update({key: value})
    op.update({'cellindex': cellIdx})
    op.update(content_dict)
    return op


def col_rename(topping:list, content:list):
    ''' rename column topping: 1'''
    opname = topping[0].split('.')[-1]
    op = {'op': opname}

    # deal with content
    Content = list_split_cond(content, '/ec/'.__eq__)
    # remove empty
    TContent = [x for x in Content if x]

    for value in TContent:
        res = dict(item.split("=") for item in value)
        op.update(res)
    return op


def single_edit(topping:list, content:list):
    ''' single edit column topping: 1'''
    opname = topping[0].split('.')[-1]
    op = {'op': opname}

    # deal with content
    Content = list_split_cond(content, '/ec/'.__eq__)
    # remove empty
    TContent = [x for x in Content if x]

    content_dict = dict()
    for value in TContent:
        res = dict(item.split("=") for item in value)
        row_idx = int(res['row'])
        cell_idx = int(res['cell'])
        idx = (row_idx, cell_idx)
        res_dict = {str(idx): res}
        content_dict.update(res_dict)
        content_dict.update({'cellindex': cell_idx})
        content_dict.update({'rowindex': row_idx})
    op.update(content_dict)
    return op


def col_split(topping:list, content:list):
    ''' split column topping: 1'''
    opname = topping[0].split('.')[-1]
    op = {'op': opname}

    idx = 0
    mid_idx = 0
    while idx < len(content):
        line = content[idx]
        if re.match(r'^columnNameCount=\d+$', line):
            column_name_count = int(line.rsplit('=', 1)[1])
            column_names = content[idx+1:idx+1+column_name_count]
            op.update({'columnNameCount': column_name_count})
            op.update({'NewColumnNames': column_names})
            idx += column_name_count
        elif re.match(r'^rowIndexCount=\d+$', line):
            row_index_count = int(line.rsplit('=', 1)[1])
            op.update({'rowIndexCount': row_index_count })
            idx += row_index_count
        elif re.match(r'^tupleCount=\d+$', line): # tuplecount idx = 0
            tuplecount = int(line.rsplit('=', 1)[1]) # 3
            # print(idx)
            idx += 1
            for _ in range(tuplecount): # 0,1,2
                length = int(content[idx: idx+1][0]) # 1,2 [1]; [3,4] 【2]; [6,7] 2
                idx += length+1 # idx = 3; idx = 6; idx =9
                mid_idx = idx

        idx += 1

    # [st_idx , end_idx] : middle sub text
    st_idx = mid_idx
    ed_idx = 0
    newlist = []
    oldlist = []
    while mid_idx < len(content):
        line = content[mid_idx]

        if re.match(r'^newRowCount=\d+$', line):
            ed_idx = mid_idx
            newRowCount = int(line.rsplit('=', 1)[1])
            newjsonfile = content[mid_idx + 1: mid_idx + 1 + newRowCount]

            for newjson in newjsonfile:
                new = json.loads(newjson)
                newlist.append(new)

            # jump to old row
            next_idx = mid_idx + 1 + newRowCount
            next_line = content[next_idx]
            if next_line != f'oldRowCount={newRowCount}':
                raise ValueError("something wrong")
            # oldlist = []
            oldjsonfile = content[next_idx+1: next_idx + 1+ newRowCount]

            # for i in range(newRowCount):
            #     new = json.loads(newjsonfile[i])
            #     pprint(new)
            #     old = json.loads(oldjsonfile[i])
            #     pprint(old)
            #     for d1, d2 in zip(old['cells'], new['cells']):
            #         print(d1['v'], d2['v'])

            for oldjson in oldjsonfile:
                jsonout = json.loads(oldjson)
                oldlist.append(jsonout)

            # old_new = zip(oldlist, newlist)

            mid_idx += newRowCount+newRowCount+1

        elif re.match(r'^\w+=.*$', line):
            res = line.split('=')
            op.update({res[0]: res[1]})

        mid_idx += 1

    for line in content[st_idx: ed_idx]:
        res = line.split('=')
        op.update({res[0]: res[1]})

    ''' ZIP new and old and get the difference '''
    rowIndexCount = int(op['rowIndexCount'])
    removeOriginalColumn = op['removeOriginalColumn']
    firstNewCellIndex = int(op['firstNewCellIndex']) # 6
    columncount = op['columnNameCount'] #2
    target_len = firstNewCellIndex + columncount
    cellindex_list = list(range(firstNewCellIndex,target_len,1))

    # original column being splited information
    oricolumn = json.loads(op['column'])
    # if the original column gets removed, change the null to "v": null
    # if removed, also changed; else no change
    cellindex = int(oricolumn['cellIndex'])

    newres = []
    oldres = []
    if removeOriginalColumn == 'true':
        # remove original
        # add null to new list, if the null in new list
        cellindex_list.append(cellindex)
        for newvalues in newlist:
            newcells = pad_or_truncate(newvalues['cells'],target_len)
            if not newcells[cellindex]:
                newcells[cellindex] = {"v": None}
            newres.append(pad_or_truncate(newcells, target_len))

        for oldvalues in oldlist:
            oldcells = oldvalues['cells']
            if not oldcells[cellindex]:
                oldcells[cellindex] = {"v": None}
            for _ in range(columncount):
                oldcells.append({"v": None})
            oldres.append(pad_or_truncate(oldcells, target_len))

        # print([(x, y) for x, y in pairs if x != y])
        # for d1, d2 in zip(oldres, newres):
        #     print([(x,y) for x,y in ])

    elif removeOriginalColumn == 'false':
        # keep original
        for newvalues in newlist:
            newcells = newvalues['cells']
            if not newcells[cellindex]:
                newcells[cellindex] = {"v": None}
            newres.append(pad_or_truncate(newcells, target_len))
        for oldvalues in oldlist:
            oldcells = oldvalues['cells']
            if not oldcells[cellindex]:
                oldcells[cellindex] = {"v": None}
            # for _ in range(columncount):
            #     oldcells.append({"v": None})
            oldres.append(pad_or_truncate(oldcells, target_len))
            # oldres.append(oldcells)

    pairs = list(zip(oldres, newres))
    for row in range(rowIndexCount):
        pair = list(pairs[row])
        d1, d2 = pair
        compare_list(d1, d2, row, op)

    op.update({'cellidx_list': cellindex_list})
    # deal with json file
    '''
    1. first new column index: firstNewCellIndex
    2. new column count : columnNameCount
    3. row index : rowIndexCount len(zip)
    '''
    return op


def row_reorder(topping, content):
    opname = topping[0].split('.')[-1]
    op = {'op': opname}
    idx = 0
    while idx < len(content):
        line = content[idx]
        if re.match(r'^rowIndexCount=\d+', line):
            rowIndexCount = int(line.rsplit('=', 1)[1])
            op.update({'rowIndexCount': rowIndexCount})
            row_idx = content[idx+1: idx+1+rowIndexCount]
            op.update({'row-index': row_idx})
            idx+=rowIndexCount
        idx+=1

    return op


def row_flag(top, content):
    opname = top[0].split('.')[-1]
    op = {'op': opname}
    res = dict(item.split("=") for item in top[1:])
    op.update(res)
    return op


def row_star(top, content):
    opname = top[0].split('.')[-1]
    op = {'op': opname}
    res = dict(item.split("=") for item in top[1:])
    op.update(res)
    return op


def column_move(top, content):
    ''' move column '''
    opname = top[0].split('.')[-1]
    op = {'op': opname}
    res = dict(item.split("=") for item in top[1:])
    op.update(res)
    return op


def reconciliation():
    pass


func_map ={
    'MassCellChange': Common_transform,
    'ColumnAdditionChange': col_addition,
    'ColumnRemovalChange': col_remove,
    'ColumnRenameChange': col_rename,
    'CellChange': single_edit,
    'ColumnSplitChange': col_split,
    'MassRowColumnChange': transpose_cols_rows,
    'RowReorderChange': row_reorder,
    'RowFlagChange': row_flag,
    'RowStarChange': row_star,
    'ColumnMoveChange': column_move,
    'ReconChange': reconciliation,

}

name_map ={
    'MassCellChange': 4,
    'ColumnAdditionChange': 5,
    'ColumnRemovalChange': 3,
    'ColumnRenameChange': 1,
    'CellChange':1,
    'ColumnSplitChange': 1,
    'MassRowColumnChange': 1,
    'RowReorderChange': 1,
    'RowFlagChange': 4,
    'RowStarChange': 4,
    'ColumnMoveChange': 5,
}
# mass row column change : transpose
# row reorder
# row removal
# row flag
# row star
# column reorder


def main():
    args = Options.get_args()
    #
    # filepath =f'research_data/TAPP_data/changes/{args.file_path}/transpose_chan.txt'
    filepath = f'research_data/data2/history/{args.file_path}/change.txt'
    # filepath = f'research_data/data2/history/1591944670566.change/transpose_chan.txt'
    # filepath = 'research_data/TAPP_data/changes/1591864798279.change/transpose_chan.txt'
    with open(filepath, 'r')as f:
        # txt = f.read()
          data = f.readlines()

        # data = txt.split('\n/ec/\n')
    data = [x.strip() for x in data]
    # different text file has different number of topping

    # top_count = args.num_top ; initialize
    top_count = 3

    # mapping to different function
    opname = data[1].split('.')[-1]

    top_count = name_map[opname]
    # if opname == 'MassCellChange':
    #     top_count = 4
    # elif opname == 'ColumnAdditionChange':
    #     top_count = 5
    # elif opname == 'ColumnRemovalChange':
    #     top_count = 3
    # elif opname == 'CellChange':
    #     top_count = 1
    # elif opname == 'ColumnRenameChange':
    #     top_count = 1
    # elif opname == 'ColumnSplitChange':
    #     top_count = 1

    head, top, content = data[0], data[1:top_count + 1], data[top_count + 1:]

    # common transformation : upper/lower/...
    log_folder = args.log
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    prov_path = f'{log_folder}/{args.out}'
    # prov_path = 'log/prov9.json'
    op = func_map[opname](top, content)

    with open(prov_path, "w") as outfile:
        json.dump(op, outfile, indent=4)


if __name__ == '__main__':
    main()