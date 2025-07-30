

import customtkinter as ctk
from tkinter import ttk, messagebox
import db_logic as db
import os

DB_FILE = 'nainai_tea.db'

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("奶茶店进销存管理系统")
        self.geometry("1200x750")

        # Initialize selected product state
        self.selected_product_id = None
        self.selected_product_name = None
        
        # For auto-refresh
        self.db_file_path = DB_FILE
        self.last_db_mod_time = 0

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_view = ctk.CTkTabview(container)
        self.tab_view.pack(fill="both", expand=True)

        self.tab_pos = self.tab_view.add("实时销售 (POS)")
        self.tab_inventory = self.tab_view.add("库存管理")
        self.tab_products = self.tab_view.add("产品与配方")
        self.tab_reports = self.tab_view.add("数据报表")

        # Create UI structure
        self.create_pos_tab()
        self.create_inventory_tab()
        self.create_products_tab()
        self.create_reports_tab()

        # Initial data load and start monitoring
        self.refresh_all_data()
        self.start_monitoring_db()

    def check_for_db_changes(self):
        """Checks if the database file has been modified."""
        try:
            mod_time = os.path.getmtime(self.db_file_path)
            if mod_time != self.last_db_mod_time:
                print(f"Database change detected at {mod_time}. Refreshing UI.")
                self.last_db_mod_time = mod_time
                self.refresh_all_data()
        except OSError:
            # Handle case where file might not exist yet or is inaccessible
            pass
        finally:
            # Schedule the next check
            self.after(1000, self.check_for_db_changes)

    def start_monitoring_db(self):
        """Initiates the database monitoring loop."""
        # Set the initial modification time
        try:
            self.last_db_mod_time = os.path.getmtime(self.db_file_path)
        except OSError:
            self.last_db_mod_time = 0
        
        # Start the checking loop
        self.check_for_db_changes()

    def refresh_all_data(self):
        """Global function to refresh all data across all tabs."""
        print("Refreshing all application data...")
        current_selection = self.inv_tree.focus()
        current_product_selection = self.selected_product_id

        self.refresh_pos_products()
        self.refresh_inventory_list()
        self.refresh_product_list()
        self.refresh_reports()
        
        if current_selection:
            self.inv_tree.focus(current_selection)
            self.inv_tree.selection_set(current_selection)
        
        if current_product_selection:
            self.show_recipe_for_product(self.selected_product_id, self.selected_product_name)

        print("All data refreshed.")

    # ------------------ POS Tab ------------------
    def create_pos_tab(self):
        self.current_order = {}
        pos_frame = ctk.CTkFrame(self.tab_pos)
        pos_frame.pack(fill="both", expand=True)

        self.pos_product_frame = ctk.CTkScrollableFrame(pos_frame, label_text="选择产品")
        self.pos_product_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        order_frame = ctk.CTkFrame(pos_frame, width=350)
        order_frame.pack(side="right", fill="y", padx=10, pady=10)
        order_label = ctk.CTkLabel(order_frame, text="当前订单", font=ctk.CTkFont(size=16, weight="bold"))
        order_label.pack(pady=10)
        self.order_tree = ttk.Treeview(order_frame, columns=("name", "qty", "price"), show="headings")
        self.order_tree.heading("name", text="商品"); self.order_tree.heading("qty", text="数量"); self.order_tree.heading("price", text="小计")
        self.order_tree.column("qty", width=60, anchor="center"); self.order_tree.column("price", width=80, anchor="e")
        self.order_tree.pack(fill="both", expand=True, padx=10)
        self.total_label = ctk.CTkLabel(order_frame, text="总计: ¥0.00", font=ctk.CTkFont(size=14))
        self.total_label.pack(pady=10)
        order_actions_frame = ctk.CTkFrame(order_frame)
        order_actions_frame.pack(pady=10)
        submit_btn = ctk.CTkButton(order_actions_frame, text="下单", command=self.submit_order)
        submit_btn.pack(side="left", padx=10)
        clear_btn = ctk.CTkButton(order_actions_frame, text="清空", command=self.clear_order)
        clear_btn.pack(side="left", padx=10)

    def refresh_pos_products(self):
        for widget in self.pos_product_frame.winfo_children():
            widget.destroy()
        products = db.get_all_products()
        for pid, name, price in products:
            btn_text = f"{name}\n(¥{price:.2f})"
            btn = ctk.CTkButton(self.pos_product_frame, text=btn_text, command=lambda p=pid, n=name, pr=price: self.add_to_order(p, n, pr))
            btn.pack(fill="x", padx=10, pady=5)

    def add_to_order(self, product_id, name, price):
        if product_id in self.current_order: self.current_order[product_id]["qty"] += 1
        else: self.current_order[product_id] = {"name": name, "qty": 1, "price": price}
        self.update_order_display()

    def update_order_display(self):
        for i in self.order_tree.get_children(): self.order_tree.delete(i)
        total = 0
        for pid, data in self.current_order.items():
            subtotal = data["qty"] * data["price"]
            self.order_tree.insert("", "end", values=(data["name"], data["qty"], f"{subtotal:.2f}"))
            total += subtotal
        self.total_label.configure(text=f"总计: ¥{total:.2f}")

    def clear_order(self):
        self.current_order = {}; self.update_order_display()

    def submit_order(self):
        if not self.current_order:
            messagebox.showwarning("空订单", "订单中没有任何商品。"); return
        success_all = True
        for product_id, data in self.current_order.items():
            success, message = db.process_sale(product_id, data['qty'])
            if not success:
                messagebox.showerror("下单失败", f"处理 '{data['name']}' 时出错: {message}"); success_all = False; break
        if success_all:
            messagebox.showinfo("成功", "订单已成功处理！"); self.clear_order()

    # ------------------ Inventory Tab ------------------
    def create_inventory_tab(self):
        inv_frame = ctk.CTkFrame(self.tab_inventory); inv_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("id", "name", "stock", "unit", "low_stock")
        self.inv_tree = ttk.Treeview(inv_frame, columns=columns, show="headings")
        self.inv_tree.heading("id", text="ID"); self.inv_tree.heading("name", text="原料名称"); self.inv_tree.heading("stock", text="当前库存")
        self.inv_tree.heading("unit", text="单位"); self.inv_tree.heading("low_stock", text="低库存阈值"); self.inv_tree.column("id", width=50)
        self.inv_tree.pack(fill="both", expand=True, padx=10, pady=10)
        action_frame = ctk.CTkFrame(inv_frame); action_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(action_frame, text="添加新原料", command=self.add_ingredient_window).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="更新库存", command=self.update_stock_window).pack(side="left", padx=5)

    def refresh_inventory_list(self):
        for i in self.inv_tree.get_children(): self.inv_tree.delete(i)
        for item in db.get_all_ingredients(): self.inv_tree.insert("", "end", values=item)

    def add_ingredient_window(self):
        win = ctk.CTkToplevel(self); win.title("添加新原料"); win.geometry("400x350")
        ctk.CTkLabel(win, text="原料名称:").pack(pady=(10,0)); name_entry = ctk.CTkEntry(win, width=300); name_entry.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(win, text="初始库存数量:").pack(pady=(10,0)); stock_entry = ctk.CTkEntry(win); stock_entry.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(win, text="单位 (例如: kg, L, 个):").pack(pady=(10,0)); unit_entry = ctk.CTkEntry(win); unit_entry.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(win, text="低库存阈值:").pack(pady=(10,0)); threshold_entry = ctk.CTkEntry(win); threshold_entry.pack(pady=5, padx=20, fill="x")
        def save_ingredient():
            try: stock = float(stock_entry.get()); threshold = float(threshold_entry.get())
            except ValueError: messagebox.showerror("输入错误", "库存和阈值必须是数字。", parent=win); return
            if not all([name_entry.get(), unit_entry.get()]): messagebox.showerror("输入错误", "所有字段都不能为空。", parent=win); return
            success, message = db.add_ingredient(name_entry.get(), stock, unit_entry.get(), threshold)
            if success: messagebox.showinfo("成功", message, parent=win); win.destroy()
            else: messagebox.showerror("失败", message, parent=win)
        ctk.CTkButton(win, text="保存", command=save_ingredient).pack(pady=20); win.transient(self); win.grab_set()

    def update_stock_window(self):
        selected_item = self.inv_tree.focus()
        if not selected_item: messagebox.showwarning("未选择", "请先在列表中选择一个要更新的原料。"); return
        item_values = self.inv_tree.item(selected_item, "values"); ing_id, ing_name = item_values[0], item_values[1]
        win = ctk.CTkToplevel(self); win.title(f"更新 '{ing_name}' 库存"); win.geometry("300x180")
        ctk.CTkLabel(win, text=f"为 '{ing_name}' 添加入库数量:").pack(pady=(10,0)); qty_entry = ctk.CTkEntry(win); qty_entry.pack(pady=5, padx=10, fill="x")
        def save_stock_update():
            try:
                qty_change = float(qty_entry.get())
                if qty_change <= 0: raise ValueError
            except ValueError: messagebox.showerror("输入错误", "请输入一个正数。", parent=win); return
            success, message = db.update_ingredient_stock(ing_id, qty_change)
            if success: messagebox.showinfo("成功", message, parent=win); win.destroy()
            else: messagebox.showerror("失败", message, parent=win)
        ctk.CTkButton(win, text="确认入库", command=save_stock_update).pack(pady=20); win.transient(self); win.grab_set()

    # ------------------ Products & Recipes Tab ------------------
    def create_products_tab(self):
        prod_frame = ctk.CTkFrame(self.tab_products); prod_frame.pack(fill="both", expand=True, padx=10, pady=10)
        left_panel = ctk.CTkFrame(prod_frame); left_panel.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(left_panel, text="产品列表").pack(pady=5)
        self.product_list_frame = ctk.CTkScrollableFrame(left_panel); self.product_list_frame.pack(fill="both", expand=True, pady=5)
        ctk.CTkButton(left_panel, text="添加新产品", command=self.add_product_window).pack(pady=10)
        right_panel = ctk.CTkFrame(prod_frame); right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.recipe_label = ctk.CTkLabel(right_panel, text="请先在左侧选择一个产品", font=ctk.CTkFont(size=14)); self.recipe_label.pack(pady=10)
        self.recipe_tree = ttk.Treeview(right_panel, columns=("ing_name", "qty", "unit"), show="headings")
        self.recipe_tree.heading("ing_name", text="原料"); self.recipe_tree.heading("qty", text="需要数量"); self.recipe_tree.heading("unit", text="单位")
        self.recipe_tree.pack(fill="both", expand=True, pady=5)
        self.edit_recipe_btn = ctk.CTkButton(right_panel, text="编辑配方", state="disabled", command=self.edit_recipe_window); self.edit_recipe_btn.pack(pady=10)

    def refresh_product_list(self):
        for widget in self.product_list_frame.winfo_children(): widget.destroy()
        self.products_data = db.get_all_products()
        for pid, name, price in self.products_data:
            btn = ctk.CTkButton(self.product_list_frame, text=f"{name} (¥{price:.2f})", command=lambda p=pid, n=name: self.show_recipe_for_product(p, n))
            btn.pack(fill="x", padx=5, pady=2)
        # Clear recipe view as product list has changed
        self.clear_recipe_view()

    def clear_recipe_view(self):
        self.selected_product_id = None
        self.selected_product_name = None
        self.recipe_label.configure(text="请先在左侧选择一个产品")
        for i in self.recipe_tree.get_children(): self.recipe_tree.delete(i)
        self.edit_recipe_btn.configure(state="disabled")

    def show_recipe_for_product(self, product_id, product_name):
        self.selected_product_id, self.selected_product_name = product_id, product_name
        self.recipe_label.configure(text=f"'{product_name}' 的配方")
        for i in self.recipe_tree.get_children(): self.recipe_tree.delete(i)
        recipe_data = db.get_recipe_for_product(product_id)
        for _, name, qty, unit in recipe_data: self.recipe_tree.insert("", "end", values=(name, qty, unit))
        self.edit_recipe_btn.configure(state="normal")

    def add_product_window(self):
        win = ctk.CTkToplevel(self); win.title("添加新产品"); win.geometry("300x200")
        ctk.CTkLabel(win, text="产品名称:").pack(pady=(10,0)); name_entry = ctk.CTkEntry(win); name_entry.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(win, text="产品价格 (¥):").pack(pady=(10,0)); price_entry = ctk.CTkEntry(win); price_entry.pack(pady=5, padx=10, fill="x")
        def save_product():
            name, price_str = name_entry.get(), price_entry.get()
            if not name or not price_str: messagebox.showerror("输入错误", "名称和价格不能为空。", parent=win); return
            try: price = float(price_str)
            except ValueError: messagebox.showerror("输入错误", "价格必须是数字。", parent=win); return
            success, message = db.add_product(name, price)
            if success: messagebox.showinfo("成功", message, parent=win); win.destroy()
            else: messagebox.showerror("失败", message, parent=win)
        ctk.CTkButton(win, text="保存", command=save_product).pack(pady=20); win.transient(self); win.grab_set()

    def edit_recipe_window(self):
        win = ctk.CTkToplevel(self)
        win.title(f"编辑 '{self.selected_product_name}' 的配方")
        win.geometry("500x600")

        current_recipe = {item[0]: item[2] for item in db.get_recipe_for_product(self.selected_product_id)}
        all_ingredients = db.get_all_ingredients()
        
        scrollable_frame = ctk.CTkScrollableFrame(win, label_text="选择原料并输入用量")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.recipe_vars = {}
        for ing_id, name, _, unit, _ in all_ingredients:
            frame = ctk.CTkFrame(scrollable_frame)
            frame.pack(fill="x", pady=2)

            var = ctk.BooleanVar()
            check = ctk.CTkCheckBox(frame, text=f"{name} ({unit})", variable=var)
            check.pack(side="left", padx=5)

            entry = ctk.CTkEntry(frame, width=100)
            entry.pack(side="right", padx=5)

            if ing_id in current_recipe:
                var.set(True)
                entry.insert(0, str(current_recipe[ing_id]))
            
            # Store name along with var and entry to prevent crashes
            self.recipe_vars[ing_id] = {"var": var, "entry": entry, "name": name}

        def save_recipe_changes():
            new_recipe_list = []
            for ing_id, data in self.recipe_vars.items():
                if data["var"].get():  # If checkbox is checked
                    qty_str = data["entry"].get()
                    ing_name = data["name"]  # Use the stored name, this is safer

                    if not qty_str:
                        messagebox.showerror("输入错误", f"请为选中的原料 '{ing_name}' 输入用量。", parent=win)
                        return
                    try:
                        qty = float(qty_str)
                        if qty <= 0:
                            raise ValueError
                        new_recipe_list.append((ing_id, qty))
                    except ValueError:
                        messagebox.showerror("输入错误", f"原料 '{ing_name}' 的用量必须是一个正数。", parent=win)
                        return
            
            success, message = db.save_recipe(self.selected_product_id, new_recipe_list)
            if success:
                messagebox.showinfo("成功", message, parent=win)
                self.show_recipe_for_product(self.selected_product_id, self.selected_product_name)
                win.destroy()
            else:
                messagebox.showerror("失败", message, parent=win)

        save_btn = ctk.CTkButton(win, text="保存配方", command=save_recipe_changes)
        save_btn.pack(pady=10)

        win.transient(self)
        win.grab_set()

    # ------------------ Reports Tab ------------------
    def create_reports_tab(self):
        reports_frame = ctk.CTkFrame(self.tab_reports); reports_frame.pack(fill="both", expand=True, padx=10, pady=10)
        summary_frame = ctk.CTkFrame(reports_frame); summary_frame.pack(fill="x", pady=10)
        self.today_sales_label = ctk.CTkLabel(summary_frame, text="今日销售额: ¥0.00", font=ctk.CTkFont(size=16)); self.today_sales_label.pack(side="left", padx=20, pady=10)
        self.today_orders_label = ctk.CTkLabel(summary_frame, text="今日订单数: 0", font=ctk.CTkFont(size=16)); self.today_orders_label.pack(side="left", padx=20, pady=10)
        details_frame = ctk.CTkFrame(reports_frame); details_frame.pack(fill="both", expand=True, pady=10)
        ranking_frame = ctk.CTkFrame(details_frame); ranking_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(ranking_frame, text="畅销产品榜").pack()
        self.ranking_tree = ttk.Treeview(ranking_frame, columns=("name", "qty", "total"), show="headings")
        self.ranking_tree.heading("name", text="产品名称"); self.ranking_tree.heading("qty", text="总销量"); self.ranking_tree.heading("total", text="总销售额")
        self.ranking_tree.pack(fill="both", expand=True, pady=5)
        recent_frame = ctk.CTkFrame(details_frame); recent_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(recent_frame, text="近期销售记录").pack()
        self.recent_sales_tree = ttk.Treeview(recent_frame, columns=("time", "name", "qty", "price"), show="headings")
        self.recent_sales_tree.heading("time", text="时间"); self.recent_sales_tree.heading("name", text="产品"); self.recent_sales_tree.heading("qty", text="数量"); self.recent_sales_tree.heading("price", text="金额")
        self.recent_sales_tree.column("time", width=150); self.recent_sales_tree.pack(fill="both", expand=True, pady=5)

    def refresh_reports(self):
        orders, sales = db.get_today_summary()
        self.today_sales_label.configure(text=f"今日销售额: ¥{sales:.2f}")
        self.today_orders_label.configure(text=f"今日订单数: {orders}")
        for i in self.ranking_tree.get_children(): self.ranking_tree.delete(i)
        for name, qty, total in db.get_product_sales_ranking(): self.ranking_tree.insert("", "end", values=(name, qty, f"{total:.2f}"))
        for i in self.recent_sales_tree.get_children(): self.recent_sales_tree.delete(i)
        for time, name, qty, price in db.get_recent_sales(): self.recent_sales_tree.insert("", "end", values=(time, name, qty, f"{price:.2f}"))

if __name__ == "__main__":
    app = App()
    app.mainloop()
