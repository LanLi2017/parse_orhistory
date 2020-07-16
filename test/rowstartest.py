from pprint import pprint


def row_star(top,content):
    opname = top[0].split('.')[-1]
    op = {'op': opname}
    res = dict(item.split("=") for item in top[1:])
    op.update(res)
    return op


filepath = f'row_star.txt'
# filepath = f'research_data/data2/history/1591944670566.change/transpose_chan.txt'
# filepath = 'research_data/TAPP_data/changes/1591864798279.change/transpose_chan.txt'
with open(filepath, 'r')as f:
    # txt = f.read()
    data = f.readlines()

# data = txt.split('\n/ec/\n')
data = [x.strip() for x in data]
# different text file has different number of topping

# top_count = args.num_top ; initialize
top_count = 4
head, top, content = data[0], data[1:top_count + 1], data[top_count + 1:]
op = row_star(top, content)
pprint(op)