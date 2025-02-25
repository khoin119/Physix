from os.path import dirname, join
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export
import math
import matplotlib.pyplot as plt

class Force:
    def __init__(self, name, magnitude, direction):
        self.name = name
        self.magnitude = magnitude
        self.direction = direction

    def __str__(self):
        return f"Force {self.name} (magnitude={self.magnitude}, direction={self.direction})"


class Object:
    def __init__(self, name, mass, x, y, vix=0, viy=0, v_initial=0, theta=0):
        self.name = name
        self.mass = mass
        self.x = x
        self.y = y
        self.vix = vix  
        self.viy = viy 
        self.v_initial = v_initial
        self.theta = theta  # default to 0 if not provided

    def __str__(self):
        return f"Object {self.name} (mass={self.mass}, position=({self.x}, {self.y}))"


class Event:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name}"  # return the name of the event as a string

class Run:
    def __init__(self, simulationName):
        self.simulationName = simulationName

class SimulationInterpreter:
    def __init__(self, model):
        
        self.runs = []
        for run in model.runs:
            new_run = Run(run.simulationName)
            self.runs.append(new_run)
        
        self.modelName = model.name
        
        self.objects = [] # create objects
        for obj in model.objects:
            new_object = Object(obj.name, obj.mass, obj.x, obj.y, obj.vix, obj.viy, obj.v_initial, obj.theta)
            self.objects.append(new_object)

        self.forces = [] # create forces
        for force in model.forces:
            new_force = Force(force.name, force.magnitude, force.direction)
            self.forces.append(new_force)

        self.events = [] # create events (store just the names, not Event objects)
        for event in model.events:
            self.events.append(event.name)

    def calculate(self, event_name):
        if event_name not in self.events:  # Check if event_name is valid
            print(f"Event '{event_name}' is not supported or does not exist.")
            return

        if event_name == "throwing":
            self.calculate_throwing()

        if event_name == "throwing_up":
            self.calculate_throwing_up()
            
        if event_name == "throwing_angle":
            self.calculate_throwing_angle()

        if event_name == "free_fall":
            self.calculate_free_fall()
    
    
    
    def calculate_throwing_angle(self):
    
        for object in self.objects: # find the throwing object
            if object.name.lower() != "ground" and object.name.lower() != "floor":
                throwing_object = object
                break

        if not throwing_object:
            print("Could not find throwing object.")
            return

        obj_vix = throwing_object.vix  
        obj_viy = throwing_object.viy
        obj_vo = throwing_object.v_initial
        theta = throwing_object.theta

    
        if (obj_vix == 0 or obj_viy == 0) and (obj_vo == 0 or theta == 0):
            print("Error: For a throwing angle event, the initial velocity (v_initial) and launch angle (theta) must be provided.")
            return

       
        if obj_vo != 0 and theta != 0: #calculate the horizontal and vertical components
            obj_vix = obj_vo * math.cos(theta)  # calculate horizontal velocity
            obj_viy = obj_vo * math.sin(theta)  # calculate vertical velocity

        # Proceed with the rest of the calculation
        for force in self.forces:  # Find gravity force
            if force.name.lower() == "gravity":
                gravity_force = force
                break

        if not gravity_force:
            print("Could not find gravity force.")
            return

        g = gravity_force.magnitude  # Gravitational acceleration (usually 9.81 m/s²)
        obj_ypos = throwing_object.y  # Initial height

        # Using the correct equation for total time of flight
        t_total = (obj_vo * math.sin(theta)) / g + math.sqrt((2 * (obj_ypos + (obj_vo**2 * (math.sin(theta)**2)) / (2 * g))) / g)

        # Calculate maximum height
        h_max = (obj_viy ** 2) / (2 * g)
        
        # Calculate horizontal distance
        horizontal_distance = obj_vix * t_total

        print(f"Total time of flight: {t_total:.7f} seconds")
        print(f"Maximum Height: {h_max:.7f} meters")
        print(f"Horizontal Distance: {horizontal_distance:.7f} meters")

    def calculate_throwing(self):
        
        for force in self.forces: # find gravity force
            if force.name.lower() == "gravity":
                gravity_force = force
                break
        
        for object in self.objects: # find falling object
            if object.name.lower() != "ground" and object.name.lower() != "floor":
                throwing_object = object
                break

        if not gravity_force or not throwing_object:
            print("Could not find gravity force or throwing object.")
            return

        f1 = gravity_force.magnitude
        obj_vix = throwing_object.vix
        obj_viy = throwing_object.viy
        obj_ypos = throwing_object.y
        obj_name = throwing_object.name

        t_total = math.sqrt((2 * obj_ypos) / f1 )
        x_displacement = obj_vix * t_total
        
        vxf = obj_vix
        vyf = f1 * t_total
         
        final_vel = math.sqrt((vxf ** 2) + (vyf ** 2))
        
        print(f"Total time of flight: {t_total:.7f} seconds")
        print(f"Horinzontal Displacement before hitting the ground is {x_displacement:.7} meters")
        print(f"Final velocity is {final_vel:.7} m/s")
        
        yes_no = input(f"Are you looking for {obj_name}'s horizontal displacement at specific time? (yes/no): ").lower()
        
        ty = 0
        x_pos_t = 0
        
        if yes_no in ["yes", "y"]:
            ty = float(input("At what time? (in seconds): "))
            x_pos_t = obj_vix * ty
        
            print(f"X({ty}) = {x_pos_t} meters ")
        
        
        yes_no2 = input(f"Are you looking for {obj_name}'s vertical velocity? (yes/no): ").lower()
        
        ty2 = 0
        vyt2 = 0
        
        if yes_no2 in ["yes", "y"]:
            ty2 = float(input("At what time? (in seconds): "))
            vyt2 = f1 * ty2
        
            print(f"Vy({ty2}) = {vyt2} m/s")
        
        ty3 = 0
        y_pos_t = 0
        
        yes_no3 = input(f"Are you looking for {obj_name}'s vertical displacement at specific time? (yes/no): ").lower()
        if yes_no3 in ["yes", "y"]:
            ty3 = float(input("At what time? (in seconds): "))
            y_pos_t = (1/2) * f1 * (ty3 ** 2)
        
            print(f"Y({ty3}) = {y_pos_t} meters")
        
        
        self.plot_trajectory(obj_vix, obj_viy, f1, t_total, obj_ypos) # call the plot methods
        self.plot_additional_graphs(obj_vix, obj_viy, f1, t_total, obj_ypos)

    def calculate_throwing_up(self):
        
        for force in self.forces: # find gravity force
            if force.name.lower() == "gravity":
                gravity_force = force
                break
        
        for object in self.objects: # find falling object
            if object.name.lower() != "ground" and object.name.lower() != "floor":
                throwing_object = object
                break

        if not gravity_force or not throwing_object:
            print("Could not find gravity force or throwing object.")
            return

        f1 = gravity_force.magnitude
        obj_viy = throwing_object.viy
        obj_ypos = throwing_object.y

        t_peak = obj_viy / f1
        t_total = 2 * t_peak
        h_max = obj_ypos + (obj_viy ** 2) / (2 * f1)

        print(f"Time to reach the highest point: {t_peak:.7f} seconds")
        print(f"Total time of flight: {t_total:.7f} seconds")
        print(f"Maximum height: {h_max:.7f} meters")
        
        self.plot_throw_up_graph(obj_ypos, obj_viy, f1, t_total)

    def calculate_free_fall(self):
        
        for force in self.forces: # find gravity force
            if force.name.lower() == "gravity":
                gravity_force = force
                break
        
        for object in self.objects: # find falling object
            if object.name.lower() != "ground" and object.name.lower() != "floor":
                falling_object = object
                break

        if not gravity_force or not falling_object:
            print("Could not find gravity force or falling object.")
            return

        f1 = gravity_force.magnitude
        obj1_height = falling_object.y
        obj1_name = falling_object.name

        t = math.sqrt((2 * obj1_height) / f1)
        vf = math.sqrt(2 * f1 * obj1_height)

        print(f"{obj1_name} takes {t:.7f} seconds to reach the ground.")
        print(f"The final speed of {obj1_name} is {vf:.7f} m/s.")

        yes_no = input(f"Are you looking for {obj1_name}'s position? (yes/no): ").lower()
        
        ty = 0
        height_t = 0
        
        if yes_no in ["yes", "y"]:
            try:
                ty = float(input("At what time? (in seconds): "))
                if ty < 0 or ty > t:
                    raise ValueError("Time must be between 0 and the total fall time.")
                height_t = obj1_height - (1 / 2) * f1 * (ty ** 2)
            except ValueError as e:
                print(e)
            print(f"Height of {obj1_name}: {height_t:.7f} meters at {ty:.7f} seconds.")

        self.plot_freefall_graphs(f1, t, obj1_height)


    def plot_trajectory(self, vix, viy, gravity, total_time, initial_height):
        times = []
        time_step = 0.01
        current_time = 0
        while current_time <= total_time:
            times.append(current_time)
            current_time += time_step
        
        x_positions = [vix * t for t in times]
        y_positions = [initial_height + viy * t - 0.5 * gravity * t ** 2 for t in times]

        plt.figure(figsize=(6, 5))
        plt.plot(x_positions, y_positions, label="Trajectory", marker="o", markersize=3)
        plt.title("Object Trajectory")
        plt.xlabel("Horizontal Position (m)")
        plt.ylabel("Vertical Position (m)")
        plt.grid()
        plt.legend()
        plt.show()
        
    def plot_freefall_graphs(self, gravity, total_time, obj1_height):
        times = []
        time_step = 0.01
        current_time = 0
        while current_time <= total_time:
            times.append(current_time)
            current_time += time_step
        
        height_t = [obj1_height - (1 / 2) * gravity * (t ** 2) for t in times]
        plt.figure(figsize=(6, 5))
        plt.plot(times, height_t, label="Height", marker="o", markersize=3)
        plt.title("Height vs Time")
        plt.xlabel("Time (s)")
        plt.ylabel("Vertical Position (m)")
        plt.grid()
        plt.legend()
        plt.show()
        

        y_velocities = [gravity * t for t in times]
        plt.figure(figsize=(6, 5))
        plt.plot(times, y_velocities, label="Horizontal Position", marker="o", markersize=3)
        plt.title("Speed vs Time")
        plt.xlabel("Time (s)")
        plt.ylabel("Velocity (m/s)")
        plt.grid()
        plt.legend()
        plt.show()
    

    def plot_additional_graphs(self, vix, viy, gravity, total_time, initial_height):
            times = []
            time_step = 0.01
            current_time = 0
            while current_time <= total_time:
                times.append(current_time)
                current_time += time_step
                
            # x position vs time
            x_positions = [vix * t for t in times]
            plt.figure(figsize=(6, 5))
            plt.plot(times, x_positions, label="Horizontal Position", marker="o", markersize=3)
            plt.title("Position vs Time")
            plt.xlabel("Time (s)")
            plt.ylabel("Horizontal Position (m)")
            plt.grid()
            plt.legend()
            

            #  y position vs time
            y_positions = [initial_height + viy * t - 0.5 * gravity * t ** 2 for t in times]
            plt.figure(figsize=(6, 5))
            plt.plot(times, y_positions, label="Vertical Position", marker="o", markersize=3)
            plt.title("Position vs Time")
            plt.xlabel("Time (s)")
            plt.ylabel("Vertical Position (m)")
            plt.grid()
            plt.legend()
            plt.show()

            # velocity vs time
            y_velocities = [viy - gravity * t for t in times]
            plt.figure(figsize=(6, 5))
            plt.plot(times, y_velocities, label="Vertical Velocity", marker="o", markersize=3)
            plt.title("Velocity vs Time")
            plt.xlabel("Time (s)")
            plt.ylabel("Vertical Velocity (m/s)")
            plt.grid()
            plt.legend()
            plt.show()

            # acceleration vs Time
            y_accelerations = [-gravity for t in times]  # Constant acceleration due to gravity
            plt.figure(figsize=(6, 5))
            plt.plot(times, y_accelerations, label="Vertical Acceleration", marker="o", markersize=3)
            plt.title("Acceleration vs Time")
            plt.xlabel("Time (s)")
            plt.ylabel("Vertical Acceleration (m/s²)")
            plt.grid()
            plt.legend()
            plt.show()
            
    def plot_throw_up_graph(self, initial_height, viy, gravity, total_time):
            times = []
            time_step = 0.01
            current_time = 0
            while current_time <= total_time:
                times.append(current_time)
                current_time += time_step
                
            # x position vs time
            y_positions = [initial_height + viy * t - 0.5 * gravity * t ** 2 for t in times]
            plt.figure(figsize=(6, 5))
            plt.plot(times, y_positions, label="Vertical Position", marker="o", markersize=3)
            plt.title("Vertical Position vs Time")
            plt.xlabel("Time (s)")
            plt.ylabel("Vertical Position (m)")
            plt.grid()
            plt.legend()  
            plt.show()

    def run(self):
        
        if not self.runs:
            print("Error: No 'run' command found. Simulation cannot execute.")
            return
        
        for run in self.runs: # simulation name has to exist in order to execute
            if run.simulationName == self.modelName:
                break
            else:
                # if no matching simulation name found
                print(f"Error: Simulation with that name not found.")
                return
            
        print("Running Simulation:")
        for obj in self.objects:
            print(obj)
        for force in self.forces:
            print(force)
        for event in self.events:
            print(f"Event: {event}")
    
        self.run_event() # call the run event
                


    def run_event(self):
        for event_name in self.events: # automatically run each event found in the model
            print(f"Running event: {event_name}")
            self.calculate(event_name)


def main():
    this_folder = dirname(__file__)
    physix_mm = metamodel_from_file(join(this_folder, "physix.tx"), debug=False)
    metamodel_export(physix_mm, join(this_folder, "physix_meta.dot"))

    physix_model = physix_mm.model_from_file(join(this_folder, "program.phx"))
    model_export(physix_model, join(this_folder, "program.dot"))

    interpreter = SimulationInterpreter(physix_model)
    interpreter.run()


if __name__ == "__main__":
    main()
