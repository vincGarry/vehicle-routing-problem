from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from typing import List, Optional, Tuple
import osmnx as ox
import networkx as nx
import folium
from folium import plugins
import numpy as np


def print_solution(manager, routing, solution,weights):
    """
    Prints the solution on the console.

    Args:
        manager: The routing index manager.
        routing: The routing model.
        solution: The solution obtained from the routing solver.
        names (Optional[List[str]]): List of names corresponding to node indices. Defaults to None.
    """
    print(f"Objective: {solution.ObjectiveValue()}")
    max_route_distance = 0
    for vehicle_id in range(routing.vehicles()):
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        weightsTotal = 0
        route_distance = 0
        while True:
            plan_output += f" {manager.IndexToNode(index)} -> "
            previous_index = index
            weightsTotal += weights[index if index<len(weights)-1 else 0]
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
            # print(previous_index,index)
            # print(f"{routing.IsEnd(previous_index)} {routing.IsEnd(index)}")
            if routing.IsEnd(index):
                break
        plan_output += f"{manager.IndexToNode(index)}\n"
        plan_output += f"Distance of the route: {route_distance}m"
        print(plan_output)
        print(f"total weight brought {weightsTotal}\n")
        max_route_distance = max(route_distance, max_route_distance)
    print(f"Maximum of the route distances: {max_route_distance}m")

def get_routes(solution, routing, manager):
    #save all route by the drivers
    routes,distanceBetweenPoint = [],[]
    for route_nbr in range(routing.vehicles()):
        index = routing.Start(route_nbr)
        route = [manager.IndexToNode(index)]
        distances = []
        while not routing.IsEnd(index):
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            routeDistance = routing.GetArcCostForVehicle(previous_index, index, route_nbr)
            distances.append(routeDistance)
            route.append(manager.IndexToNode(index))
        routes.append(route)
        distanceBetweenPoint.append(distances)
    return routes,distanceBetweenPoint

def optimize_routes(
    distance_matrix: List[List[int]], depot: int, driverCount : int, volume:int, weights:List[int]
) -> (List[int],List[float]):
    """
    Solves the vehicle routing problem and returns the optimized route.

    Args:
        distance_matrix (List[List[int]]): 2D list representing the distance matrix between nodes.
        depot (int): Index of the starting point.
        names (Optional[List[str]]): List of names corresponding to node indices. Defaults to None.

    Returns:
        List[int]: The optimized route as a list of node indices.
    """
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix), driverCount, depot
    )  # num of vehicles set to 1

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    #distance
    # routing.AddDimension(
    #     transit_callback_index,
    #     0,  # no slack
    #     15000,  # vehicle maximum travel distance
    #     True,  # start cumul to zero
    #     "Distance",
    # )
    # distance_dimension = routing.GetDimensionOrDie("Distance")
    # distance_dimension.SetGlobalSpanCostCoefficient(100)

    #capacity
    def demand_callback(from_index):
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return weights[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        [volume for x in range(driverCount)],  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity",
    )
    
    #search strategy finding nearest next point
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    # Print solution on console and return the optimized route.
    if solution:
        try:
            print_solution(manager,routing,solution,weights)
            route,distanceBetweenPoint = get_routes(solution,routing,manager)
            return route,distanceBetweenPoint
        except Exception as e :
            print(e)
            return [],[]
    else:
        print("gagal solve")
        return [],[]
