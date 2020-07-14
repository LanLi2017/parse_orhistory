import re
from pprint import pprint


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


def main():
    filepath = f'row_reorder_change.txt'
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

    op = row_reorder(top, content)
    pprint(op)


if __name__ == '__main__':
    main()