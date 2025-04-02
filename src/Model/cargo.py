class Cargo:
    def __init__(self, name, value_per_unit, weight, space_required, category):
        self.name = name
        self.value_per_unit = value_per_unit
        self.weight = weight
        self.space_required = space_required
        self.category = category

    def __repr__(self):
        return (f"Cargo({self.name}, Category: {self.category}, "
                f"Weight: {self.weight}, Space: {self.space_required}, "
                f"Value/Unit: {self.value_per_unit})")
