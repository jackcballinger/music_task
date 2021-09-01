import argparse
from datetime import datetime as dt
from pathlib import Path

from musicie.exercise_1_ingest_structure_pdf_royalty_statements import task_1
from musicie.exercise_3_artist_recording_universe import task_3

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exercise_number", type=int, required=True, choices=[1,3], help="Number of the exercise to run")
    parser.add_argument("--input_folder_location", type=str, required=False, default=Path(__file__).parent.parent / 'inputs', help="Location of the folder containing inputs")
    parser.add_argument("--write_mode", type=bool, required=False, default=False, help="Write to sql or not. Be aware that the --postgres_config.yaml parameter will need to be included")
    parser.add_argument("--postgres_yaml", type=str, required=False, help="Write to sql or not. Be aware that the --postgres_config.yaml parameter will need to be included")
    parser.add_argument("--output_folder_location", type=str, required=False, default=Path.home() / "Downloads" / "jack_ballinger_task_outputs", help="Write to sql or not. Be aware that the --postgres_config.yaml parameter will need to be included")

    return parser.parse_args()

def cli():
    """
    cli to run code locally
    """
    args = argument_parser()
    exercise_selected = exercise_dict[args.exercise_number]
    exercise_selected.run_exercise(
        args.input_folder_location,
        args.output_folder_location,
        args.write_mode,
        args.postgres_yaml
    )

exercise_dict = {
    1: task_1,
    3: task_3
}

if __name__ == "__main__":
    cli()
