import numpy as np
from itertools import cycle

def generate_signal_function(spec, days, slots):
    total = days * slots
    sig = np.zeros(total, dtype=int)

    def fill_block(d_idx, start, length, value):
        if start >= slots:
            d_idx += 1
            start -= slots
        if start + length > slots:
            length_first = slots - start
            sig[d_idx * slots + start: d_idx * slots + start + length_first] = value
            if d_idx + 1 < days:
                sig[(d_idx + 1) * slots: (d_idx + 1) * slots + (start + length - slots)] = value
        else:
            sig[d_idx * slots + start: d_idx * slots + start + length] = value

    # --- 共通：時間帯判定 ---
    if spec['type'] == 'day':
        sig.fill(-1)
        for d in range(days):
            start_slot = spec.get('start', 0)
            end_slot = spec.get('end', slots - 1) + 1
            sig[d * slots + start_slot: d * slots + end_slot] = 1
            if 'break_start' in spec and 'break_end' in spec:
                break_start = spec['break_start']
                break_end = spec['break_end']
                sig[d * slots + break_start: d * slots + break_end] = 0

    elif spec['type'] == 'night':
        sig.fill(-1)
        for d in range(days):
            start_slot = spec.get('start', 0)
            end_slot = spec.get('end', slots)
            fill_block(d, start_slot, slots - start_slot, 1)
            fill_block(d, 0, end_slot, 1)
            if 'break_start' in spec and 'break_end' in spec:
                break_start = spec['break_start']
                break_end = spec['break_end']
                if break_start < break_end:
                    sig[d * slots + break_start: d * slots + break_end] = 0
                else: # 日を跨ぐ休憩
                    sig[d * slots + break_start: d * slots + slots] = 0
                    if d + 1 < days:
                        sig[(d + 1) * slots: (d + 1) * slots + break_end] = 0

    elif spec['type'] == 'shift_weekend':
        for d in range(days):
            base = d * slots
            weekday = d % 7
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

    elif spec['type'] == 'shift_rotation':
        rotation_cycle = cycle(spec['shifts'])
        for d in range(days):
            shift = next(rotation_cycle)
            start_slot = shift['start']
            end_slot = shift['end']
            sig[d * slots + start_slot: d * slots + end_slot] = 1
            if 'break_start' in shift and 'break_end' in shift:
                break_start = shift['break_start']
                break_end = shift['break_end']
                sig[d * slots + break_start: d * slots + break_end] = 0

    elif spec['type'] == 'flexible':
        for d in range(days):
            weekday = d % 7
            schedule = spec['schedule'].get(weekday)
            if schedule:
                start_slot = schedule.get('start', -1)
                end_slot = schedule.get('end', -1)
                if start_slot != -1 and end_slot != -1:
                    sig[d * slots + start_slot: d * slots + end_slot] = 1
                    if 'break_start' in schedule and 'break_end' in schedule:
                        break_start = schedule['break_start']
                        break_end = schedule['break_end']
                        sig[d * slots + break_start: d * slots + break_end] = 0
                else:
                    sig[d * slots:] = 0 # 休みの日
            else:
                sig[d * slots:] = 0 # スケジュールがない場合は休み

    elif spec['type'] == 'short_time':
        sig.fill(-1)
        start_slot = spec.get('start', 0)
        end_slot = spec.get('end', slots - 1) + 1
        for d in range(days):
            sig[d * slots + start_slot: d * slots + end_slot] = 1

    elif spec['type'] == 'every_other_day':
        for d in range(days):
            if d % 2 == 0: # 奇数日のみ勤務（0日目から数える）
                start_slot = spec['on_duty']['start']
                end_slot_next_day = spec['on_duty']['end'] + slots
                sig[d * slots + start_slot: (d + 1) * slots] = 1 # 当日
                if d + 1 < days:
                    sig[(d + 1) * slots: (d + 1) * slots + end_slot_next_day % slots] = 1 # 翌日の一部
                if 'breaks' in spec['on_duty']:
                    for break_time in spec['on_duty']['breaks']:
                        break_start = break_time['start']
                        break_end = break_time['end']
                        if break_start < break_end:
                            sig[d * slots + break_start: d * slots + break_end] = 0
                        else: # 日を跨ぐ休憩
                            sig[d * slots + break_start: (d + 1) * slots] = 0
                            if d + 1 < days:
                                sig[(d + 1) * slots: (d + 1) * slots + break_end] = 0
            else:
                sig[d * slots:] = 0 # 休みの日

    else:
        raise ValueError(f"Unknown type: {spec['type']}")

    return sig