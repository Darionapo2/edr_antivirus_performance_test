import json
import pandas as pd

def analysis():
    
    merged_json_file_path = 'testdata/run_1764241504/merged_results.json'
    
    # Load JSON file
    with open(merged_json_file_path, 'r') as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # ---------------- GENERAL STATISTICS ----------------
    general_stats = df['duration_seconds'].describe()
    general_stats.to_csv('general_stats.csv', header=['value'])

    # ---------------- BY OPERATION TYPE ----------------
    stats_by_type = df.groupby('operation_type')['duration_seconds'].describe()
    stats_by_type.to_csv('stats_by_operation_type.csv')

    # ---------------- SUCCESS COUNTS ----------------
    success_counts = df['success'].value_counts()
    success_counts.to_csv('success_counts.csv', header=['count'])

    # ---------------- TOTAL TIME BY TYPE ----------------
    total_time = df.groupby('operation_type')['duration_seconds'].sum()
    total_time.to_csv('total_time_by_operation_type.csv', header=['total_duration_seconds'])

    # ---------------- FILE OPERATIONS MB/s ----------------
    df_files = df[df['file_size'].notna()].copy()
    df_files['mb'] = df_files['file_size'] / (1024 * 1024)
    df_files['mb_per_sec'] = df_files['mb'] / df_files['duration_seconds']

    df_files[['operation_id', 'operation_type', 'file_size', 'duration_seconds', 'mb_per_sec']].to_csv(
        'file_mb_per_sec.csv',
        index=False
    )

    # ---------------- AVERAGE DURATION FOR FILE OPS ----------------
    file_ops = ['copy_file', 'move_dir', 'edit_file', 'read_file', 'delete_file']
    avg_file_ops = df[df['operation_type'].isin(file_ops)].groupby('operation_type')['duration_seconds'].mean()
    avg_file_ops.to_csv('avg_duration_file_ops.csv', header=['avg_duration_seconds'])

    # ---------------- TOP 10 SLOWEST ----------------
    top10 = df.sort_values('duration_seconds', ascending=False).head(10)
    top10.to_csv('top10_slowest.csv', index=False)

    # ---------------- INTERVAL NS ----------------
    df['interval_ns'] = df['end_timestamp_ns'] - df['start_timestamp_ns']
    df[['operation_id', 'interval_ns']].to_csv('intervals_ns.csv', index=False)

    df.to_csv('testdata/run_1764241504/analytics.csv', index=False)


if __name__ == '__main__':
    analysis()
