

import inventory
import sales
import recipes

def main_menu():
    print("\n奶茶店进销存管理系统")
    print("1. 库存管理")
    print("2. 销售管理")
    print("3. 配方管理")
    print("4. 退出")
    return input("请选择操作: ")

def main():
    while True:
        choice = main_menu()
        if choice == '1':
            inventory.inventory_menu()
        elif choice == '2':
            sales.sales_menu()
        elif choice == '3':
            recipes.recipe_menu()
        elif choice == '4':
            print("感谢使用，再见！")
            break
        else:
            print("无效输入，请重新选择。")

if __name__ == "__main__":
    main()

