import tkinter as tk
from tkinter import ttk, messagebox
from config import COLOR_SCHEME, VALID_UNITS, MATERIAL_CODES
from modules.data_manager import MaterialManager
from modules.recipe_manager import RecipeManager
from modules.inventory_manager import InventoryManager


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("餐饮成本管理系统 v3.0")
        self.root.geometry("1200x800")
        self.current_dish_id = None
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton',
                        foreground=COLOR_SCHEME['text'],
                        background=COLOR_SCHEME['primary'])

        tab_control = ttk.Notebook(self.root)

        # 物料管理标签页
        material_tab = ttk.Frame(tab_control)
        self.build_material_tab(material_tab)

        # 菜品管理标签页
        dish_tab = ttk.Frame(tab_control)
        self.build_dish_tab(dish_tab)

        tab_control.add(material_tab, text="物料管理")
        tab_control.add(dish_tab, text="菜品管理")
        tab_control.pack(expand=True, fill="both")

    # region 物料管理功能
    def build_material_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 输入表单
        form_frame = ttk.LabelFrame(main_frame, text="物料信息")
        form_frame.pack(fill="x", padx=5, pady=5)

        entries = {}
        fields = [
            ("名称：", "name", 0),
            ("类型：", "type", 1, list(MATERIAL_CODES.keys())),
            ("单价：", "price", 2),
            ("单位：", "unit", 3, VALID_UNITS)
        ]

        for field in fields:
            row = field[2]
            ttk.Label(form_frame, text=field[0]).grid(row=row, column=0, padx=5, pady=5, sticky="e")
            if len(field) > 3:
                cb = ttk.Combobox(form_frame, values=field[3])
                cb.grid(row=row, column=1, sticky="ew")
                entries[field[1]] = cb
            else:
                entry = ttk.Entry(form_frame)
                entry.grid(row=row, column=1, sticky="ew")
                entries[field[1]] = entry

        # 操作按钮
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="保存物料", command=lambda: self.save_material(entries)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="采购入库", command=lambda: self.show_purchase_window(entries)).pack(side="left",
                                                                                                        padx=5)

        # 数据表格
        self.material_tree = ttk.Treeview(main_frame,
                                          columns=("ID", "名称", "类型", "单价", "单位"),
                                          show="headings"
                                          )
        for col in ["ID", "名称", "类型", "单价", "单位"]:
            self.material_tree.heading(col, text=col)
            self.material_tree.column(col, width=100, anchor="center")
        self.material_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.material_tree.bind("<Button-3>", self.show_material_menu)
        self.load_materials()

    def show_material_menu(self, event):
        item = self.material_tree.identify_row(event.y)
        if item:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="删除", command=lambda: self.delete_material(item))
            menu.post(event.x_root, event.y_root)

    def save_material(self, entries):
        try:
            data = {
                "name": entries["name"].get(),
                "material_type": entries["type"].get(),
                "unit_price": float(entries["price"].get()),
                "unit": entries["unit"].get()
            }
            if MaterialManager().add_material(**data):
                self.load_materials()
                self.load_material_options()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def delete_material(self, item):
        material_id = self.material_tree.item(item, "values")[0]
        if messagebox.askyesno("确认", "确定删除该物料吗？"):
            if MaterialManager().delete_material(material_id):
                self.load_materials()

    def load_materials(self):
        for item in self.material_tree.get_children():
            self.material_tree.delete(item)
        for mat in MaterialManager().get_all_materials():
            self.material_tree.insert("", "end", values=mat)

    def show_purchase_window(self, entries):
        win = tk.Toplevel(self.root)
        win.title("采购入库")

        material_id = entries["id"].get()
        current_stock = InventoryManager().get_current_stock(material_id)
        ttk.Label(win, text=f"当前库存：{current_stock}").grid(row=0, columnspan=2)

        ttk.Label(win, text="采购数量：").grid(row=1, column=0, padx=5, pady=5)
        quantity_entry = ttk.Entry(win)
        quantity_entry.grid(row=1, column=1)

        ttk.Label(win, text="采购单价：").grid(row=2, column=0, padx=5, pady=5)
        price_entry = ttk.Entry(win)
        price_entry.grid(row=2, column=1)

        ttk.Button(win, text="确认入库",
                   command=lambda: self.process_purchase(material_id, quantity_entry.get(), price_entry.get())) \
            .grid(row=3, columnspan=2, pady=10)

    def process_purchase(self, material_id, quantity, unit_price):
        try:
            if InventoryManager().add_purchase(material_id, float(quantity), float(unit_price)):
                messagebox.showinfo("成功", "采购记录已保存")
        except ValueError:
            messagebox.showerror("错误", "请输入有效数字")

    # endregion

    # region 菜品管理功能
    def build_dish_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)

        # 左半部分：菜品列表
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.dish_tree = ttk.Treeview(left_frame, columns=("ID", "名称", "成本"), show="headings")
        self.dish_tree.pack(fill="both", expand=True)
        self.dish_tree.bind("<<TreeviewSelect>>", self.on_dish_select)

        # 右半部分：菜品编辑
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_frame.columnconfigure(1, weight=1)
        right_frame.rowconfigure(3, weight=1)

        # 菜品信息
        ttk.Label(right_frame, text="菜品名称：").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.dish_name_entry = ttk.Entry(right_frame)
        self.dish_name_entry.grid(row=0, column=1, sticky="ew")
        ttk.Button(right_frame, text="新建菜品", command=self.create_dish).grid(row=0, column=2, padx=5)

        # 原料添加
        ttk.Label(right_frame, text="选择原料：").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.material_combobox = ttk.Combobox(right_frame)
        self.material_combobox.grid(row=1, column=1, sticky="ew")

        ttk.Label(right_frame, text="用量：").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.quantity_entry = ttk.Entry(right_frame)
        self.quantity_entry.grid(row=2, column=1, sticky="ew")
        ttk.Button(right_frame, text="添加原料", command=self.add_ingredient).grid(row=2, column=2, padx=5)

        # 原料列表
        self.ingredient_tree = ttk.Treeview(right_frame,
                                            columns=("原料ID", "名称", "单价", "用量", "小计"),
                                            show="headings"
                                            )
        self.ingredient_tree.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=10)
        self.ingredient_tree.bind("<Button-3>", self.show_ingredient_menu)

        self.load_dishes()
        self.load_material_options()

    def show_ingredient_menu(self, event):
        item = self.ingredient_tree.identify_row(event.y)
        if item:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="删除", command=lambda: self.delete_ingredient(item))
            menu.post(event.x_root, event.y_root)

    def delete_ingredient(self, item):
        ingredient_id = self.ingredient_tree.item(item, "values")[0]
        if messagebox.askyesno("确认", "确定删除该原料吗？"):
            RecipeManager().conn.execute(
                "DELETE FROM recipe_items WHERE material_id=?", (ingredient_id,)
            )
            self.update_ingredients()

    def create_dish(self):
        dish_name = self.dish_name_entry.get().strip()
        if dish_name:
            if dish_id := RecipeManager().create_dish(dish_name):
                self.load_dishes()

    def add_ingredient(self):
        if not self.current_dish_id:
            messagebox.showwarning("警告", "请先选择菜品")
            return

        selected = self.material_combobox.get().split(":")
        if len(selected) < 2:
            return

        try:
            material_id = selected[0].strip()
            quantity = float(self.quantity_entry.get())
            if RecipeManager().add_ingredient_to_dish(self.current_dish_id, material_id, quantity):
                self.update_ingredients()
        except ValueError:
            messagebox.showerror("错误", "请输入有效数字")

    def on_dish_select(self, event):
        selected = self.dish_tree.selection()
        if selected:
            self.current_dish_id = self.dish_tree.item(selected[0], "values")[0]
            self.update_ingredients()

    def load_dishes(self):
        for item in self.dish_tree.get_children():
            self.dish_tree.delete(item)
        for dish in RecipeManager().conn.execute("SELECT * FROM dishes").fetchall():
            self.dish_tree.insert("", "end", values=dish)

    def load_material_options(self):
        materials = [f"{m[0]}: {m[1]} ({m[4]})" for m in MaterialManager().get_all_materials()]
        self.material_combobox["values"] = materials

    def update_ingredients(self):
        for item in self.ingredient_tree.get_children():
            self.ingredient_tree.delete(item)

        if self.current_dish_id:
            ingredients = RecipeManager().conn.execute('''
                SELECT m.id, m.name, m.unit_price, r.quantity, m.unit
                FROM recipe_items r
                JOIN materials m ON r.material_id = m.id
                WHERE r.dish_id = ?
            ''', (self.current_dish_id,)).fetchall()

            for ing in ingredients:
                unit_price = InventoryManager().get_weighted_cost(ing[0])
                quantity = ing[3]
                total = unit_price * quantity
                self.ingredient_tree.insert("", "end", values=(
                    ing[0], ing[1], f"{unit_price}元/{ing[4]}",
                    f"{quantity}{ing[4]}", f"{total:.2f}元"
                ))
    # endregion


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()