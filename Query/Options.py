import argparse


def get_args():
    ''' Get all the args'''
    parser = argparse.ArgumentParser(description='Input the query: ')
    parser.add_argument(
        "--row",
        type=int,
        default=0,
        help='Row Index'
    )
    parser.add_argument(
        "--col",
        type=int,
        default=0,
        help='Column Index'
    )
    parser.add_argument(
        "--log",
        type=str,
        help='log folder name'
    )
    parser.add_argument(
        "--out",
        type=str,
        help='Save file name'
    )
    return parser.parse_args()