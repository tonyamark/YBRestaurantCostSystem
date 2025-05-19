import tkinter as tk
from tkinter import ttk, messagebox
from modules.data_manager import MaterialManager
from config import MATERIAL_TYPES, VALID_UNITS


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("餐饮成本管理系统 V2.0")
        self.root.geometry("1000x800")
        self.setup_ui()

    def setup_ui(self):
        """构建主界面"""
        # 主选项卡
        tab_control = ttk.Notebook(self.root)

        # 物料管理标签页
        material_tab = ttk.Frame(tab_control)
        self.build_material_tab(material_tab)

        tab_control.add(material_tab, text="物料管理")
        tab_control.pack(expand=True, fill="both")

    def build_material_tab(self, parent):
        """构建物料管理界面（支持价格更新）"""
        form_frame = ttk.LabelFrame(parent, text="物料信息")
        self.entries = {}

        # 输入控件
        fields = [
            ("物料名称：", 'name', 'entry'),
            ("物料类型：", 'type', 'combobox', list(MATERIAL_TYPES.keys())),
            ("单价（元）：", 'price', 'entry'),
            ("单位：", 'unit', 'combobox', VALID_UNITS)
        ]

        for row, (label, key, widget_type, *options) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky='e')
            if widget_type == 'entry':
                self.entries[key] = ttk.Entry(form_frame, width=25)
            elif widget_type == 'combobox':
                self.entries[key] = ttk.Combobox(form_frame, values=options[0], state="readonly")
            self.entries[key].grid(row=row, column=1, padx=5, pady=5, sticky='w')

        # 保存按钮
        ttk.Button(form_frame, text="保存", command=self.save_material).grid(row=4, columnspan=2, pady=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        # 数据表格
        columns = ("ID", "名称", "类型", "单价", "单位", "库存")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=120, anchor='center')
        self.tree.pack(expand=True, fill="both", padx=10)
        self.load_data()

    def save_material(self):
        """保存或更新物料"""
        try:
            data = {
                'name': self.entries['name'].get().strip(),
                'material_type': self.entries['type'].get(),
                'category': '',  # 可扩展分类
                'unit_price': float(self.entries['price'].get()),
                'unit': self.entries['unit'].get()
            }

            # 基础验证
            if not data['name']:
                raise ValueError("物料名称不能为空")
            if data['unit_price'] < 0:
                raise ValueError("单价不能为负数")

            manager = MaterialManager()
            result = manager.add_or_update_material(**data)

            if result:
                # 清空输入框
                self.entries['name'].delete(0, tk.END)
                self.entries['price'].delete(0, tk.END)
                self.entries['type'].set('')
                self.entries['unit'].set('')
                self.entries['name'].focus_set()

                # 刷新表格
                self.load_data()
                messagebox.showinfo("成功", f"已{result}物料：{data['name']}")

        except ValueError as e:
            messagebox.showerror("输入错误", f"请检查：\n{str(e)}")
        except Exception as e:
            messagebox.showerror("系统错误", f"操作失败：\n{str(e)}")

    def load_data(self):
        """加载表格数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        manager = MaterialManager()
        materials = manager.get_all_materials()
        for mat in materials:
            self.tree.insert("", "end", values=(
                mat[0],  # ID
                mat[1],  # 名称
                mat[2],  # 类型
                f"¥{mat[4]:.2f}",  # 单价
                mat[5],  # 单位
                f"{mat[6]} {mat[5]}"  # 库存
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()