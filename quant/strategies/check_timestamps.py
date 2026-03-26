import json

# 读取回测结果
with open('backtest_results/ma_kdj_180d_complete_20260324_084201.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("原始时间戳检查:")
print("="*60)

for symbol_code, symbol_data in data.items():
    name = symbol_data['name']
    print(f"\n{name} ({symbol_code}):")
    
    # 显示最后 3 笔交易的时间戳
    trades = symbol_data['trades']
    for i, trade in enumerate(trades[-3:], len(trades)-2):
        entry_ts = trade['entry_time']
        exit_ts = trade['exit_time']
        print(f"  交易#{i}: entry={entry_ts}, exit={exit_ts}")
        print(f"           entry 类型={type(entry_ts).__name__}")
