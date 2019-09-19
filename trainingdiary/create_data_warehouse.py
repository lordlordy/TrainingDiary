from workoutentry.data_warehouse import DataWarehouseGenerator






if __name__ == '__main__':
    generator = DataWarehouseGenerator("TestWarehouse.sqlite3")
    generator.generate()