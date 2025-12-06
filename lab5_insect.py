class Insect:
    number_of_legs = 6
    habitat = "forest"

    def __init__(self, name="Inspect", speed=0.0, mass=0.0):
        self.__name = name
        self.__speed = speed
        self.__mass = mass

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def speed(self):
        return self.__speed

    @speed.setter
    def speed(self, value):
        self.__speed = value

    @property
    def mass(self):
        return self.__mass

    @mass.setter
    def mass(self, value):
        self.__mass = value

    def __str__(self):
        return f"Insect: {self.__name}, speed: {self.__speed}, mass: {self.__mass}"

    def __repr__(self):
        return f"Insect(name={self.__name}, speed={self.__speed}, mass={self.__mass})"

    def __del__(self):
        print(f"Insect {self.__name} removed")

def main():
    
    if __name__ == "__main__":
        insect_1 = Insect("Mosquito", 1.2, 0.03)
        insect_2 = Insect("Bee", 1.2, 0.03)
        insect_3 = Insect("Beetle", 1.2, 0.03)
        
        for insect in [insect_1, insect_2, insect_3]:
            print("Name:", insect.name)
            print("Speed:", insect.speed)
            print("Mass:", insect.mass)
            print("Number of legs:", insect.number_of_legs)
            print("Habitat:", insect.habitat)
            print("Display __str__:", str(insect))
            print("Object code:", repr(insect))
            print("-" * 50)
            
if __name__ == "__main__":
    main()
    