import argparse
from pathlib import Path

from musicie.exercise_1_ingest_structure_pdf_royalty_statements import task_1
from musicie.exercise_3_artist_recording_universe import task_3


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exercise_number",
        type=int,
        required=True,
        choices=[1, 3],
        help="Number of the exercise to run",
    )
    parser.add_argument(
        "--input_folder_location",
        type=str,
        required=False,
        default=Path(__file__).parent.parent / "inputs",
        help="Location of the folder containing inputs",
    )
    parser.add_argument(
        "--write_mode",
        type=bool,
        required=False,
        default=False,
        help="Boolean flag that when true, will write output data to file",
    )
    parser.add_argument(
        "--postgres_yaml",
        type=str,
        required=False,
        default=None,
        help="Location of a postgres_config.yaml file. If specified, code will alltempt to write to sql.",
    )
    parser.add_argument(
        "--output_folder_location",
        type=str,
        required=False,
        default=Path.home() / "Downloads" / "jack_ballinger_task_outputs",
        help="Location of the folder to write outputs to",
    )

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
        args.postgres_yaml,
    )


exercise_dict = {1: task_1, 3: task_3}

if __name__ == "__main__":
    cli()
