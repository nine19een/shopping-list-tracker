[中文](README.zh-CN.md) / **ENG**

# Shopping List Tracker

A small Tkinter desktop app for household purchases, with a Chinese interface. Add items and prices, then drag rows between 待选 (Candidate), 未购买 (To Buy), and 已购买 (Purchased). Each column shows item counts, costs, and live selection totals.

## Run

Use Python 3.11+ with Tkinter and a graphical desktop. From the repository directory:

```bash
python list.py
```

The app uses only Python's standard library. No account or initial data file is required.

## Use and data

1. Enter a nonempty item name and a nonnegative, finite numeric price, labeled in yuan (元), then click 添加到清单. New items enter 待选.
2. Drag an item's row into another column to change its state. Checkboxes show selection totals and enable 删除勾选 (delete selected); checking an item does not change its state.

总预算 sums all items, including purchased items. Amounts display two decimal places, while stored prices retain their entered decimal precision.

Adding, moving, or deleting items saves `shopping_tracker_data.json` in your home directory; the app loads it on startup. Checkbox selections are not saved.

Save failures are silent, invalid JSON is ignored, and malformed records can stop loading. Keep your own backup; there is no undo. Use finite prices: `NaN` can raise an error and `Infinity` is currently accepted.

## Optional executable

Packaging requires a separate PyInstaller installation:

```bash
python -m PyInstaller --noconsole --onefile --name "统计清单" list.py
```

The documented Windows output is `dist/统计清单.exe`; this build has not been tested here. The packaged app uses the same home-directory data file. Keep generated data, `dist/`, `build/`, and `__pycache__/` out of version control.

## License

[MIT](LICENSE), copyright © 2025 nine19een.
