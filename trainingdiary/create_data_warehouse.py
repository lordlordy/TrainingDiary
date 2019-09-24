from workoutentry.data_warehouse import DataWarehouseGenerator






if __name__ == '__main__':
    generator = DataWarehouseGenerator("training_data_warehouse.sqlite3")
    generator.generate(print_progress=True)