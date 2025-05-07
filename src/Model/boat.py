class Boat:
    def __init__(self, name, max_weight, max_space, total_value=0):
        self.name = name
        self.max_weight = max_weight
        self.max_space = max_space
        self.current_weight = 0
        self.current_space = 0
        self.total_value = 0
        self.cargo_list = []

    def can_load(self, cargo):
        if self.current_weight + cargo.weight > self.max_weight:
            print(f"Cannot load {cargo.name}: weight limit exceeded.")
            return False
        if self.current_space + cargo.space_required > self.max_space:
            print(f"Cannot load {cargo.name}: space limit exceeded.")
            return False
        self.cargo =+ cargo.value_per_unit
        return True

    def load_cargo(self, cargo):
        if self.can_load(cargo):
            self.cargo_list.append(cargo)
            self.current_weight += cargo.weight
            self.current_space += cargo.space_required
            self.total_value += cargo.value_per_unit
            print(f"Cargo '{cargo.name}' loaded successfully.")
        else:
            print(f"Failed to load cargo '{cargo.name}'.")

    def __repr__(self):
        return (f"Boat({self.name}, Weight Capacity: {self.max_weight}, "
                f"Space Capacity: {self.max_space}, "
                f"Current Weight: {self.current_weight}, Current Space: {self.current_space})")
