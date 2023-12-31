import argparse
from handler.application import Application
from config import STRATEGY_NAME


def main():
    parser = argparse.ArgumentParser(description='Your Application Description')
    parser.add_argument('--num-vals-table', type=int, default=None, help='Number of visible rows in the table')

    args = parser.parse_args()

    app = Application(num_vals_table=args.num_vals_table, data_name=STRATEGY_NAME)
    app.run()


if __name__ == "__main__":
    main()
