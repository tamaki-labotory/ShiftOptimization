#!/usr/bin/env python3
import argparse
import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from generate_signal import generate_signal_function as gsf

def load_config(path):
    """
    Load YAML config defining days, slots, and subjects specs.
    """
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description='Generate and visualize work/rest signals using CWT prep.'
    )
    parser.add_argument('config', help='Path to problem definition YAML')
    parser.add_argument('--days', type=int,
                        help='Override number of days from config')
    parser.add_argument('--slots', type=int,
                        help='Override slots per day from config')
    args = parser.parse_args()

    # Load problem definition
    cfg = load_config(args.config)
    days = args.days or cfg.get('days')
    slots = args.slots or cfg.get('slots')
    specs = cfg.get('subjects', {})

    # Generate raw signals
    signals = {name: gsf(spec, days, slots) for name, spec in specs.items()}

    # Reshape into matrix form (days x slots)
    matrices = {name: sig.reshape(days, slots) for name, sig in signals.items()}

    # Plot setup
    n = len(matrices)
    fig, axes = plt.subplots(n, 1, figsize=(7, 3*n), sharex=True)
    if n == 1:
        axes = [axes]

    # Colormap for -1,0,1
    cmap = mcolors.ListedColormap(['#d73027', '#cccccc', '#1a9850'])
    bounds = [-1.5, -0.5, 0.5, 1.5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    # Day labels
    day_labels = np.arange(1, 8)

    # Plot each subject
    for ax, (name, mat) in zip(axes, matrices.items()):
        im = ax.imshow(mat[:7], aspect='auto', cmap=cmap, norm=norm)
        ax.set_title(f'Subject {name}', fontsize=12)
        ax.set_ylabel('Day', fontsize=10)
        ax.set_yticks(np.arange(7))
        ax.set_yticklabels(day_labels, fontsize=8)

    # X-axis hours
    axes[-1].set_xlabel('Hour of Day', fontsize=10)
    xticks = np.arange(-0.5, 24.5, 24/slots)  # slots + 1 に変更
    axes[-1].set_xticks(xticks)
    axes[-1].set_xticklabels(xticks+0.5, fontsize=8)
    axes[-1].set_xlim(-0.5, slots-0.5) # Add this line

    # Colorbar
    plt.tight_layout(rect=[0, 0, 0.88, 1])
    cbar_ax = fig.add_axes([0.90, 0.10, 0.02, 0.8])
    cbar = fig.colorbar(im, cax=cbar_ax, ticks=[-1, 0, 1])
    cbar.ax.set_yticklabels(['Rest', 'Neutral', 'Work'], fontsize=8)

    plt.show()

if __name__ == '__main__':
    main()
