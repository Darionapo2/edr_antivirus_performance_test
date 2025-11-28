import json
import pandas as pd


def analysis():

    test_run = 'run_2025-11-28_14-59-47'

    merged_json_file_path = f'testdata/{test_run}/merged_results.json'
    save_folder = f'testdata/{test_run}'

    # Load JSON file
    with open(merged_json_file_path, 'r') as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Create a GLOBAL unique operation id combining instance + operation_id
    df['global_op_id'] = df['instance'] + "_" + df['operation_id'].astype(str)

    # ---------------- GENERAL STATISTICS (all instances) ----------------
    df['duration_seconds'].describe().to_csv(f'{save_folder}/general_stats.csv', header=['value'])

    # ---------------- BY OPERATION TYPE (all instances) ----------------
    df.groupby('operation_type')['duration_seconds'].describe().to_csv(f'{save_folder}/stats_by_operation_type.csv')

    # ---------------- BY INSTANCE ----------------
    df.groupby('instance')['duration_seconds'].describe().to_csv(f'{save_folder}/stats_by_instance.csv')

    # ---------------- BY INSTANCE + TYPE ----------------
    df.groupby(['instance', 'operation_type'])['duration_seconds'].describe().to_csv(f'{save_folder}/stats_by_instance_and_type.csv')

    # ---------------- SUCCESS COUNTS ----------------
    df['success'].value_counts().to_csv(f'{save_folder}/success_counts.csv', header=['count'])

    # ---------------- SUCCESS COUNT BY INSTANCE ----------------
    df.groupby('instance')['success'].value_counts().unstack(fill_value=0).to_csv(f'{save_folder}/success_counts_by_instance.csv')

    # ---------------- TOTAL TIME BY TYPE ----------------
    df.groupby('operation_type')['duration_seconds'].sum().to_csv(f'{save_folder}/total_time_by_operation_type.csv',
                                                                  header=['total_duration_seconds'])

    # ---------------- TOTAL TIME BY INSTANCE ----------------
    df.groupby('instance')['duration_seconds'].sum().to_csv(f'{save_folder}/total_time_by_instance.csv',
                                                            header=['total_duration_seconds'])

    # ---------------- TOTAL TIME BY INSTANCE + TYPE ----------------
    df.groupby(['instance', 'operation_type'])['duration_seconds'].sum().to_csv(f'{save_folder}/total_time_by_instance_and_type.csv',
                                                                                header=['total_duration_seconds'])

    # ---------------- FILE OPERATIONS MB/s ----------------
    df_files = df[df['file_size'].notna()].copy()

    df_files['mb'] = df_files['file_size'] / (1024 * 1024)
    df_files['mb_per_sec'] = df_files['mb'] / df_files['duration_seconds']

    df_files[['global_op_id', 'instance', 'operation_type', 'file_size', 'duration_seconds', 'mb_per_sec']].to_csv(
        'file_mb_per_sec.csv', index=False)

    # ---------------- AVG DURATION FOR FILE OPS ----------------
    file_ops = ['copy_file', 'move_dir', 'edit_file', 'read_file', 'delete_file']

    # Global average
    df[df['operation_type'].isin(file_ops)].groupby('operation_type')['duration_seconds'].mean().to_csv(
        'avg_duration_file_ops.csv', header=['avg_duration_seconds'])

    # Per instance average
    df[df['operation_type'].isin(file_ops)].groupby(['instance', 'operation_type'])['duration_seconds'].mean().to_csv(
        'avg_duration_file_ops_by_instance.csv', header=['avg_duration_seconds'])

    # ---------------- TOP 10 SLOWEST (global) ----------------
    df.sort_values('duration_seconds', ascending=False).head(10).to_csv(f'{save_folder}/top10_slowest.csv', index=False)

    # ---------------- TOP 10 SLOWEST PER INSTANCE ----------------
    for inst, subdf in df.groupby('instance'):
        subdf.sort_values('duration_seconds', ascending=False).head(10).to_csv(f'top10_slowest_{inst}.csv', index=False)

    # ---------------- INTERVAL NS ----------------
    df['interval_ns'] = df['end_timestamp_ns'] - df['start_timestamp_ns']

    df[['global_op_id', 'instance', 'interval_ns']].to_csv(f'{save_folder}/intervals_ns.csv', index=False)

    # TODO: aggiungere statistiche by dimensione del file e operazione (statistiche server, istanza, operazione, dimensione file)
    # TODO: Statistiche filtrate per operazioni che hanno avuto successo
    # TODO: stampare in csv i dettagli per ogni operazione (raw) del json


if __name__ == '__main__':
    analysis()
