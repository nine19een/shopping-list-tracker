import json
import tkinter as tk
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tkinter import messagebox, ttk


class ShoppingTracker:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("购物清单统计")
        self.items = []
        self.data_path = Path.home() / "shopping_tracker_data.json"
        self.drag_item = None

        self.name_var = tk.StringVar()
        self.price_var = tk.StringVar()

        self._build_layout()
        self._load_items()
        self.update_totals()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        form = ttk.LabelFrame(self.root, text="添加物品")
        form.grid(column=0, row=0, sticky="ew", padx=12, pady=(12, 6))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="物品名称").grid(column=0, row=0, padx=(8, 4), pady=6, sticky="w")
        name_entry = ttk.Entry(form, textvariable=self.name_var)
        name_entry.grid(column=1, row=0, padx=(4, 8), pady=6, sticky="ew")

        ttk.Label(form, text="价格(元)").grid(column=0, row=1, padx=(8, 4), pady=6, sticky="w")
        price_entry = ttk.Entry(form, textvariable=self.price_var)
        price_entry.grid(column=1, row=1, padx=(4, 8), pady=6, sticky="ew")

        add_btn = ttk.Button(form, text="添加到清单", command=self.add_item)
        add_btn.grid(column=0, row=2, columnspan=2, pady=(4, 8))

        lists_box = ttk.Frame(self.root)
        lists_box.grid(column=0, row=1, sticky="nsew", padx=12, pady=(0, 6))
        lists_box.columnconfigure(0, weight=1)
        lists_box.columnconfigure(1, weight=1)
        lists_box.columnconfigure(2, weight=1)
        lists_box.rowconfigure(0, weight=1)

        column_definitions = [
            ("candidate", "待选"),
            ("pending", "未购买"),
            ("purchased", "已购买"),
        ]

        self.columns: dict[str, dict[str, object]] = {}

        for idx, (state, title) in enumerate(column_definitions):
            box = ttk.LabelFrame(lists_box, text=title)
            box.grid(column=idx, row=0, sticky="nsew", padx=(0 if idx == 0 else 6, 0 if idx == len(column_definitions) - 1 else 6))
            box.columnconfigure(0, weight=1)

            list_frame = ttk.Frame(box)
            list_frame.pack(fill="both", expand=True, padx=8, pady=(8, 0))

            stats_frame = ttk.Frame(box)
            stats_frame.pack(fill="x", padx=8, pady=(4, 2))

            total_label = ttk.Label(stats_frame, text="总计：0 件 / 0.00 元")
            total_label.pack(anchor="w")

            selected_label = ttk.Label(stats_frame, text="勾选：0 件 / 0.00 元")
            selected_label.pack(anchor="w", pady=(2, 0))

            actions_frame = ttk.Frame(box)
            actions_frame.pack(fill="x", padx=8, pady=(0, 8))

            delete_btn = ttk.Button(
                actions_frame,
                text="删除勾选",
                command=lambda s=state: self.delete_selected(s),
                state="disabled",
            )
            delete_btn.pack(anchor="w", pady=2, fill="x")

            self.columns[state] = {
                "box": box,
                "container": list_frame,
                "total_label": total_label,
                "selected_label": selected_label,
                "action_buttons": [delete_btn],
            }

        totals_box = ttk.LabelFrame(self.root, text="实时统计")
        totals_box.grid(column=0, row=2, sticky="ew", padx=12, pady=(0, 12))
        totals_box.columnconfigure(0, weight=1)

        self.total_cost_label = ttk.Label(totals_box, text="总预算：0.00 元")
        self.total_cost_label.grid(column=0, row=0, sticky="w", padx=8, pady=4)

        self.total_count_label = ttk.Label(totals_box, text="物品总数：0 件")
        self.total_count_label.grid(column=0, row=1, sticky="w", padx=8, pady=(4, 8))

        name_entry.focus()

    def _load_items(self) -> None:
        if not self.data_path.exists():
            return

        try:
            data = json.loads(self.data_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        valid_states = {"candidate", "pending", "purchased"}

        for entry in data:
            try:
                name = entry["name"]
                price = Decimal(entry["price"])
            except (KeyError, InvalidOperation):
                continue

            state = entry.get("state")
            if state not in valid_states:
                state = "purchased" if entry.get("purchased") else "pending"

            item = {
                "name": name,
                "price": price,
                "state": state,
                "selected": tk.BooleanVar(value=False),
                "frame": None,
            }
            self.items.append(item)
            self._render_item(item)

    def _save_items(self) -> None:
        data = [
            {
                "name": item["name"],
                "price": str(item["price"]),
                "state": item["state"],
                "purchased": item["state"] == "purchased",
            }
            for item in self.items
        ]

        try:
            self.data_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def _render_item(self, item: dict) -> None:
        frame = item.get("frame")
        if frame is not None:
            frame.destroy()

        column = self.columns[item["state"]]
        parent = column["container"]

        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)
        frame.columnconfigure(1, weight=1)

        check = ttk.Checkbutton(
            frame,
            variable=item["selected"],
            command=lambda i=item: self._on_item_select(i)
        )
        check.grid(column=0, row=0, padx=(0, 6))

        name_label = ttk.Label(frame, text=item["name"])
        name_label.grid(column=1, row=0, sticky="w")
        price_label = ttk.Label(frame, text=f"{item['price']:.2f} 元")
        price_label.grid(column=2, row=0, padx=(8, 0))

        for widget in (frame, name_label, price_label):
            widget.bind("<ButtonPress-1>", lambda e, i=item: self._start_drag(e, i))
            widget.bind("<B1-Motion>", lambda e, i=item: self._drag_motion(e, i))
            widget.bind("<ButtonRelease-1>", lambda e, i=item: self._end_drag(e, i))

        item["frame"] = frame

    def _on_item_select(self, item: dict) -> None:
        self.update_totals()

    def _update_action_buttons(self) -> None:
        for state, column in self.columns.items():
            has_selection = any(
                itm["state"] == state and itm["selected"].get() for itm in self.items
            )
            for button in column["action_buttons"]:
                if has_selection:
                    button.state(["!disabled"])
                else:
                    button.state(["disabled"])

    def _start_drag(self, event, item: dict) -> None:
        if isinstance(event.widget, ttk.Checkbutton):
            return
        self.drag_item = item
        self.root.configure(cursor="hand2")

    def _drag_motion(self, event, item: dict) -> None:
        if self.drag_item is item:
            self.root.configure(cursor="hand2")

    def _end_drag(self, event, item: dict) -> None:
        if self.drag_item is not item:
            return

        self.drag_item = None
        self.root.configure(cursor="")

        target_state = self._state_from_position(event.x_root, event.y_root)
        if target_state and target_state != item["state"]:
            item["state"] = target_state
            item["selected"].set(False)
            self._render_item(item)
            self.update_totals()
            self._save_items()

    def _state_from_position(self, x_root: int, y_root: int) -> str | None:
        widget = self.root.winfo_containing(x_root, y_root)
        while widget is not None:
            for state, column in self.columns.items():
                if widget == column["box"]:
                    return state
            widget = widget.master
        return None

    def delete_selected(self, state: str) -> None:
        remaining = []
        removed = False
        for item in self.items:
            if item["state"] == state and item["selected"].get():
                removed = True
                if item.get("frame") is not None:
                    item["frame"].destroy()
            else:
                remaining.append(item)
        if removed:
            self.items = remaining
            self.update_totals()
            self._save_items()

    def add_item(self) -> None:
        name = self.name_var.get().strip()
        price_text = self.price_var.get().strip()

        if not name:
            messagebox.showerror("输入错误", "请填写物品名称。")
            return

        if not price_text:
            messagebox.showerror("输入错误", "请填写价格。")
            return

        try:
            price = Decimal(price_text)
        except InvalidOperation:
            messagebox.showerror("输入错误", "价格格式不正确，请输入数字。")
            return

        if price < 0:
            messagebox.showerror("输入错误", "价格不能为负数。")
            return

        item = {
            "name": name,
            "price": price,
            "state": "candidate",
            "selected": tk.BooleanVar(value=False),
            "frame": None,
        }
        self.items.append(item)
        self._render_item(item)
        self.name_var.set("")
        self.price_var.set("")
        self.update_totals()
        self._save_items()

    def update_totals(self) -> None:
        total_cost = sum((item["price"] for item in self.items), Decimal("0"))
        total_count = len(self.items)

        self.total_cost_label.config(text=f"总预算：{total_cost:.2f} 元")
        self.total_count_label.config(text=f"物品总数：{total_count} 件")

        for state, column in self.columns.items():
            state_items = [item for item in self.items if item["state"] == state]
            state_cost = sum((item["price"] for item in state_items), Decimal("0"))
            state_count = len(state_items)
            column["total_label"].config(text=f"总计：{state_count} 件 / {state_cost:.2f} 元")

            selected_items = [
                item for item in state_items if item["selected"].get()
            ]
            selected_cost = sum((item["price"] for item in selected_items), Decimal("0"))
            selected_count = len(selected_items)
            column["selected_label"].config(
                text=f"勾选：{selected_count} 件 / {selected_cost:.2f} 元"
            )

        self._update_action_buttons()


def main() -> None:
    root = tk.Tk()
    ShoppingTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
