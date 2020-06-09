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
        "--prov",
        type=str,
        help='Save file name'
    )
    return parser.parse_args()