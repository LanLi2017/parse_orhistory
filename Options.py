import argparse


def get_args():
    ''' Get all the args'''
    parser = argparse.ArgumentParser(description='Parser of OpenRefine Provenance Model')
    # parser.add_argument(
    #     "--num_top",
    #     type= int,
    #     default= 4,
    #     help='number of toppings'
    # )
    parser.add_argument(
        "--file_path",
        type=str,
        # choices=['1591062762131.change', '1591063332588.change', '1591063264316.change', '1591063379500.change', '1591063129144.change', '1591317229023.change', '1591863373048.change', '1591863680781.change','1591864798279.change'],
        default='1591062762131.change',
        help='path of the input change'
    )
    parser.add_argument(
        "--log",
        type = str,
        default='log',
        help='path of the log folder'
    )
    parser.add_argument(
        "--out",
        type=str,
        default='prov1.json',
        help='output provenance file name'
    )
    return parser.parse_args()