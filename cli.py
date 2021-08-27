import argparse
from datetime import datetime as dt
from pathlib import Path

import exercise_1_ingest_structure_pdf_royalty_statements

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exercise_number", type=int, required=True, choices=[1,3], help="Number of the exercise to run")
    parser.add_argument("--write_data_to_sql", type=bool, required=False, help="Write to sql or not. Be aware that the --postgres_config.yaml parameter will need to be included")
    parser.add_argument("--postgres_yaml", type=str, required=False, help="Write to sql or not. Be aware that the --postgres_config.yaml parameter will need to be included")
    parser.add_argument("--output_location", type='str', required=False, default=Path.home() / "Downloads" / f"{parser.parse_args().exercise_number}_data" / dt.today().strftime("Y%m%dT%H%M%S"), help="Location to write output to if write_data_to_sql is not selected")
    parser.add_argument("--input_folder_location", type='str', required=False, help="Location of the folder containing inputs")

    return parser.parse_args()

def cli():
    """
    cli to run code locally
    """

    args = argument_parser()


if __name__ == "__main__":
    cli()
