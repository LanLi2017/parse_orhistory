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
        res_dict = {idx: res}
        content_dict.update(res_dict)
    op.update(content_dict)
    pprint(op)
    # column name
    # for equation in content[1:]:
    #     print(equation)
    #     # try:
    #     res = dict(equation.split('='))
    #     print(res)
    #     # except:
        #     pass


func_map ={
    'MassCellChange': Common_transform,
}


def main():
    filepath = 'prov/-1_trans_change.txt'
    with open(filepath, 'r')as f:
        # txt = f.read()
          data = f.readlines()

        # data = txt.split('\n/ec/\n')
    data = [x.strip() for x in data]
    # different text file has different number of topping
    top_count = 4
    head, top, content = data[0], data[1:top_count+1], data[top_count+1:]

    # mapping to different function
    opname = top[0].split('.')[-1]

    # common transformation : upper/lower/...
    func_map[opname](top, content)


if __name__ == '__main__':
    main()