class GreaterNoidaMetro:
    def __init__(self):
        # Ordered list of stations on the Greater Noida Metro line
        self.stations = [
            "Alpha",
            "Beta",
            "Gamma",
            "Delta",
            "Epsilon",
            "Zeta",
            "Eta",
            "Theta",
            "Iota",
            "Kappa",
        ]
        
        # Fare structure based on the number of stations traveled
        # Format: (max_stations_in_range, fare_in_rupees)
        self.fare_table = [
            (2, 10),   # Up to 2 stations: ₹10
            (5, 20),   # Up to 5 stations: ₹20
            (10, 30),  # Up to 10 stations: ₹30
        ]

    def calculate_fare(self, start_station, end_station):
        if start_station not in self.stations:
            raise ValueError(f"Start station '{start_station}' not found.")
        if end_station not in self.stations:
            raise ValueError(f"End station '{end_station}' not found.")

        start_index = self.stations.index(start_station)
        end_index = self.stations.index(end_station)
        stations_traveled = abs(end_index - start_index)
        if stations_traveled == 0:
            return 0  # same station, no fare

        # Determine fare based on stations traveled using fare_table
        for max_stations, fare in self.fare_table:
            if stations_traveled <= max_stations:
                return fare
        
        # If traveled stations more than max in fare_table, charge highest fare
        return self.fare_table[-1][1]

    def get_stations(self):
        return self.stations


def main():
    print("Welcome to the Greater Noida Metro Fare Calculator (Range-wise)")
    metro = GreaterNoidaMetro()

    print("\nStations on the Greater Noida Metro line:")
    for station in metro.get_stations():
        print(f"- {station}")

    while True:
        start_station = input("\nEnter the starting station (or type 'exit' to quit): ").strip()
        if start_station.lower() == 'exit':
            print("Exiting the Greater Noida Metro Fare Calculator. Goodbye!")
            break

        end_station = input("Enter the ending station: ").strip()
        if end_station.lower() == 'exit':
            print("Exiting the Greater Noida Metro Fare Calculator. Goodbye!")
            break

        try:
            fare = metro.calculate_fare(start_station, end_station)
            if fare == 0:
                print(f"You are already at {start_station}. No fare needed.")
            else:
                print(f"Total Fare from {start_station} to {end_station}: ₹{fare}")
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
   main()

