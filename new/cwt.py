import yaml
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.colors import Normalize
import pywt
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from generate_signal import generate_signal_function as gsf


def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)


#### CWTの時間-周波数平面におけるパワーをプロットする関数 ####
def plot_cwt(signals, days, slots, clip_quantile, levels):
    total = days * slots
    t = np.arange(total)
    dt = 24 / slots
    scales = np.arange(1, 250)

    fig, axes = plt.subplots(len(signals), 1, figsize=(10, 8), sharex=True)
    for ax, (name, sig) in zip(axes, signals.items()):
        coeffs, freqs = pywt.cwt(sig, scales, 'morl')
        power = coeffs
        vmin = np.quantile(power, 0)
        vmax = np.quantile(power, clip_quantile)
        norm = Normalize(vmin=vmin, vmax=vmax)

        im = ax.contourf(
            t,
            scales*dt/pywt.central_frequency('morl'),
            power,
            levels=np.linspace(vmin, vmax, levels),
            norm=norm
        )
        ax.plot(t, [24]*total, color='red', linewidth=0.5)
        ax.text(0, 24, '24', color='red', fontsize=10, ha='right', va='center')

        ax.xaxis.set_major_locator(MultipleLocator(24))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x/24)}'))
        ax.set_ylabel('Length of Cycle(hours)')
        ax.set_title(f'CWT Power Scalogram of Subject {name}')

    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('Wavelet Power')

    axes[-1].set_xlabel('Day')
    fig.subplots_adjust(right=0.9)
    plt.show()

#### CWTの位相をプロットする関数 ####
def plot_cwt_phase(signals, days, slots):
    total = days * slots
    t = np.arange(total)
    dt = 24 / slots
    scales = np.arange(1,250)

    phase_matrices = {}
    for name, sig in signals.items():
        coeffs, _ = pywt.cwt(sig, scales, 'morl', sampling_period=dt)
        phase_matrices[name] = np.angle(coeffs)

    fig, axes = plt.subplots(len(signals), 1, figsize=(12, 9), sharex=True)
    for ax, (name, phase_matrix) in zip(axes, phase_matrices.items()):
        pcm = ax.pcolormesh(
            t,
            scales*dt/pywt.central_frequency('morl'),
            phase_matrix,
            shading='auto',
            vmin=-np.pi,
            vmax=np.pi
        )
        ax.set_ylabel('Length of Cycle(hours)')
        ax.set_title(f'CWT Phase of Subject {name}')
        ax.plot(t, [24]*total, color='red', linewidth=0.5)
        ax.text(0, 24, '24', color='red', fontsize=10, ha='right', va='center')
        ax.xaxis.set_major_locator(MultipleLocator(24))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x/24)}'))

    axes[-1].set_xlabel('Day')
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(pcm, cax=cbar_ax)
    cbar.set_label('Phase')
    cbar.set_ticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
    cbar.set_ticklabels([r'$-\pi$', r'$-\pi/2$', r'$0$', r'$\pi/2$', r'$\pi$'])
    plt.show()

#### CWTの積分値をプロットする関数 ####
def plot_cwt_integrated(signals, days, slots):
    total = days * slots
    t = np.arange(total)
    dt = 24 / slots
    scales = np.arange(1, 250)
    cf = pywt.central_frequency('morl')
    periods = scales * dt / cf

    integrated_power = {}
    for name, sig in signals.items():
        coeffs, _ = pywt.cwt(sig, scales, 'morl')
        power = np.abs(coeffs)**2
        integrated_power[name] = np.sum(power, axis=1) * dt

    fig, axes = plt.subplots(len(signals), 1, figsize=(10, 8), sharex=True)
    for ax, name in zip(axes, signals.keys()):
        ax.plot(periods, integrated_power[name], lw=1.5)
        ax.set_xscale('log')
        ax.set_ylabel('Integrated Wavelet Power')
        ax.set_title(f'Integrated CWT of Subject {name}')
        ax.grid(True, which='both', ls='--', lw=0.5)
        ax.axvline(24, color='red', lw=1)
        ax.text(24, ax.get_ylim()[0]*1.1, '24', color='red', fontsize=10, ha='center')
        if name == 'C':
            ax.axvline(168, color='red', lw=1)
            ax.text(168, ax.get_ylim()[0]*1.1, '168', color='red', fontsize=10, ha='center')

    axes[-1].set_xlabel('Length of Cycle(hours)')
    fig.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(
        description='Solve CWT on defined problem and plot results'
    )
    parser.add_argument('config', help='Path to problem definition YAML')
    parser.add_argument('--clip-quantile', type=float, default=0.975,
                        help='Upper quantile for color clipping')
    parser.add_argument('--levels', type=int, default=30,
                        help='Number of contour levels')
    parser.add_argument('--subjects', nargs='*', default=None,
                        help='List of subject keys to include')
    parser.add_argument('--mode', choices=['power','phase','integrated'], default='power',
                        help='Plot mode')
    args = parser.parse_args()

    cfg = load_config(args.config)
    days = cfg['days']
    slots = cfg['slots']
    specs = cfg['subjects']
    if args.subjects:
        specs = {k: v for k, v in specs.items() if k in args.subjects}

    # generate_signalを外部モジュールから呼び出し
    signals = {name: gsf(spec, days, slots) for name, spec in specs.items()}

    if args.mode == 'power':
        plot_cwt(signals, days, slots, args.clip_quantile, args.levels)
    elif args.mode == 'phase':
        plot_cwt_phase(signals, days, slots)
    elif args.mode == 'integrated':
        plot_cwt_integrated(signals, days, slots)
    else:
        print(f"Unknown mode: {args.mode}")

if __name__ == '__main__':
    main()