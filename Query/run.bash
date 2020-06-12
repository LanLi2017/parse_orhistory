python answer.py --row 0 --col 1 --log log2 --out res0
python answer.py --row 1 --col 6 --log log2 --out res1
python answer.py --row 1 --col 3 --log log2 --out res2
python answer.py --row 2 --col 5 --log log2 --out res3

#sequence of number
#index transformation first;
#
#1
#x:1
#y:3
#old: 10
#new: 11
#
#2
#x:2
#Y:4
#old: "niko"
#new: "lan"
#
#3
#x:2
#y:4
#old: "lan"
#new: "niko"
#
#celltran(4,2,2,"niko","lan",0)
#celltran(4,2,3,"lan","niko",2)
#
#
#celltran(rowno,colno,change_id,old_value,new_value,parent_id)