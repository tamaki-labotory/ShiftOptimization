import yaml
import argparse


def default_config():
    return {
        'days': 30,
        'slots': 24,
        'subjects': {
            'A': {'type': 'day', 'start': 9, 'end': 17},
            'B': {'type': 'night', 'start': 20, 'end': 5},
            'C': {'type': 'shift_weekend'}
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Generate a problem definition YAML for CWT analysis'
    )
    parser.add_argument(
        '--output', '-o', default='problem.yaml',
        help='Path to output YAML definition file'
    )
    args = parser.parse_args()

    config = default_config()
    with open(args.output, 'w') as f:
        yaml.dump(config, f)
    print(f'Problem definition written to {args.output}')


if __name__ == '__main__':
    main()