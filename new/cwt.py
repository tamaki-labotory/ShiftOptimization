import yaml
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.colors import Normalize
import pywt


def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)


def generate_signal(spec, days, slots):
    total = days * slots
    sig = np.zeros(total, dtype=int)
    if spec['type'] == 'day':
        sig.fill(-1)
        for d in range(days):
            start = (d * slots) + spec['start']
            end = (d * slots) + spec['end'] + 1
            sig[start:end] = 1
    elif spec['type'] == 'night':
        sig.fill(-1)
        for d in range(days):
            base = d * slots
            # evening
            sig[base + spec['start']: base + slots] = 1
            # early morning next day
            next_end = spec['end']
            sig[base: base + next_end] = 1
    elif spec['type'] == 'shift_weekend':
        sig = np.zeros(total, dtype=int)
        for d in range(days):
            weekday = d % 7
            base = d * slots
            if weekday < 3:
                sig[base + 6: base + 12] = 1
                sig[base: base + 6] = -1
                sig[base + 12: base + 24] = -1
            elif weekday < 5:
                sig[base + 12: base + 18] = 1
                sig[base: base + 12] = -1
                sig[base + 18: base + 24] = -1
            else:
                sig[base: base + 24] = 0
    else:
        raise ValueError(f"Unknown type: {spec['type']}")
    return sig

#### CWTの時間-周波数平面におけるパワーをプロットする関数 ####
def plot_cwt(signals, days, slots, args):
    total = days * slots
    t = np.arange(total)
    dt = 24 / slots
    scales = np.arange(1, 250)

    fig, axes = plt.subplots(len(signals), 1, figsize=(10, 8), sharex=True)
    for ax, (name, sig) in zip(axes, signals.items()):
        coeffs, freqs = pywt.cwt(sig, scales, 'morl')
        power = np.abs(coeffs)**2
        vmin = np.quantile(power, 0)
        vmax = np.quantile(power, 0.975)
        norm = Normalize(vmin=vmin, vmax=vmax)

        im = ax.contourf(
            t,
            scales*dt/pywt.central_frequency('morl'), #スケールを中心周波数で除すことで周期に変換
            power,
            levels=np.linspace(vmin, vmax, 30),
            vmin=vmin,
            vmax=vmax,
            norm=norm
        )
        ax.plot(t, [24]*total, color='red', linewidth=0.5) # 24時間のラインを追加
        ax.text(0, 24, '24', color='red', fontsize=10, ha='right', va='center')  # 24の位置に赤文字を追加

        # if name == 'C':
        #     ax.plot(t, [168]*total, color='red', linewidth=0.5) # 24時間のラインを追加
        #     ax.text(0, 168, '168', color='red', fontsize=10, ha='right', va='center')  # 24の位置に赤文字を追加

        ax.xaxis.set_major_locator(MultipleLocator(24))
        ax.xaxis.set_major_formatter(FuncFormatter(
            lambda x, pos: f'{int(x/24)}'
        ))
        ax.set_ylabel('Length of Cycle(hours)')
        ax.set_title(f'CWT Scalogram of Subject {name}')


    # ── カラーバー用の独立した Axes を追加 ──
    # [left, bottom, width, height] の割合で指定（0〜1）
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('Wavelet Power')

    axes[2].set_xlabel('Day')
    fig.subplots_adjust(right=0.9)  # 本体 axes を右側へ少し縮める
    plt.show()

#### CWTの位相をプロットする関数 ####
def plot_cwt_phase(signals, days, slots, args):
    total = days * slots
    t = np.arange(total)
    dt = 24 / slots
    scales = np.arange(1,250)
    cf = pywt.central_frequency('morl')
    periods = scales * dt / cf

    # 各信号の位相行列を計算
    phase_matrices = {}
    for name, sig in signals.items():
        coeffs, _ = pywt.cwt(sig, scales, 'morl', sampling_period=dt)
        phase_matrices[name] = np.angle(coeffs)

    # プロット設定
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True, sharey=True)
    for ax, (name, phase_matrix) in zip(axes, phase_matrices.items()):
        pcm = ax.pcolormesh(
            t,
            periods,
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
        ax.xaxis.set_major_formatter(FuncFormatter(
            lambda x, pos: f'{int(x/24)}'
        ))
    axes[-1].set_xlabel('Day')

    # レイアウト調整で右側に余白を確保(例: 0.85まで)
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    # カラーバーを右側に独立配置 (余白内に配置)
    cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(pcm, cax=cbar_ax, orientation='vertical')
    cbar.set_label('Phase')
    cbar.set_ticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
    cbar.set_ticklabels([r'$-\pi$', r'$-\pi/2$', r'$0$', r'$\pi/2$', r'$\pi$'])

    plt.show()

#### CWTの積分値をプロットする関数 ####
def plot_cwt_integralated(signals, days, slots, args):
    total = days * slots
    t = np.arange(total)
    dt = 24 / slots
    scales = np.arange(1, 250)
    central_freq = pywt.central_frequency('morl')
    periods = scales * dt / central_freq

    # 結果格納用
    integrated_power = {}

    for name, sig in signals.items():
        coeffs, freqs = pywt.cwt(sig, scales, 'morl')
        power = np.abs(coeffs)**2
        # 時間方向に積分（離散積分なので sum×dt で近似）
        integrated_power[name] = np.sum(power, axis=1) * dt

    # --- プロット ---
    fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

    fig, axes = plt.subplots(len(signals), 1, figsize=(10, 8), sharex=True)
    for ax, name in zip(axes, ['A', 'B', 'C']):
        ax.plot(periods, integrated_power[name], lw=1.5)
        ax.set_xscale('log')
        ax.set_ylabel('Integrated Wavelet Power')
        ax.set_title(f'Subject {name}')
        ax.grid(True, which='both', ls='--', lw=0.5)
        ax.axvline(24,color='red', lw=1) # 24時間のラインを追加
        ax.text(24, -ax.get_ylim()[1] * 0.1, '24', color='red', fontsize=10, ha='center', va='center')  # 24の位置に赤文字を追加
        if name == 'C':
            ax.axvline(168,color='red', lw=1) # 24時間のラインを追加
            ax.text(168, -ax.get_ylim()[1] * 0.1, '168', color='red', fontsize=10, ha='center', va='center')    # 168時間のラインを追加
        
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
                        help='List of subject keys to include (e.g. A B)')
    args = parser.parse_args()

    cfg = load_config(args.config)
    days = cfg['days']
    slots = cfg['slots']
    specs = cfg['subjects']
    if args.subjects:
        specs = {k: v for k, v in specs.items() if k in args.subjects}

    signals = {name: generate_signal(spec, days, slots) for name, spec in specs.items()}
    plot_cwt_phase(signals, days, slots, args)
    # plot_cwt(signals, days, slots, args)


if __name__ == '__main__':
    main()