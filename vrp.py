import pandas as pd
import numpy as np
from sklearn.cluster import KMeans as kmeans
from src.api_osmr import get_matrix, parse_coordinates,parse_coordinates2
from src.routing import optimize_routes
from flask import Flask,request
import json

app = Flask(__name__)

@app.route("/kmeans", methods=['POST'])
def kmeans():
    dictRequest = request.json
    

@app.route("/vrp", methods=['POST'])
def routing():
    dictRequest = request.json
    coordinates = parse_coordinates2(dictRequest.get("data"))
    coordinates = ",".join(str(x) for x in reversed(dictRequest.get("storeLocation"))) +";"+coordinates
    response_distances = get_matrix(coordinates)
    distances = np.array(response_distances["distances"]).astype(int)
    weights = [0]+[x["volume"] for x in dictRequest.get("data")]
    
    best_route,distanceBetweenPoint = optimize_routes(distances,0,len(dictRequest.get("driverAssigned")),dictRequest.get("volume"),weights)
    # print(best_route)
    # print(distanceBetweenPoint)
    result =[]
    for route in best_route:
        result.append({"data":[ dictRequest.get("data")[idx-1] for idx in route[1:len(route)-2] ]})

    for idx in range(len(result)):
        result[idx]["driverAssigned"] = dictRequest.get("driverAssigned")[idx]
        for x in range(len(distanceBetweenPoint[idx])-2):
            result[idx].get("data")[x]["distance"] = f"{distanceBetweenPoint[idx][x]} km"
    return result

# @app.route("/")
# def vrp():
#     # Iterate over each unique city in the places data
#     for city in places.city.unique()[-1:]:
#         print(f"Planning route for {city}")

#         # Select the first 10 points of sales for the current city
#         df_city = places[places.city == city][:5].reset_index(drop=True)
        
#         # Parse coordinates for the selected points of sales
#         coordinates = parse_coordinates(df_city)
#         # Get the distance matrix for the selected points of sales using the OSRM API
#         response_distances = get_matrix(coordinates)

#         # Convert the distances to integer values (required by ortools)
#         distances = np.array(response_distances["distances"]).astype(int)
        
#         # Setting the farthest point as the start point
#         # Calculate the median tuple for the distance matrix
#         coordinates_tuples = np.array(response_distances["distances"]).astype(int)
        
#         median_tuple = tuple(np.median(np.array(coordinates_tuples), axis=0))
        
#         # Calculate the Euclidean distance of each tuple from the median tuple
#         distances_tuples = [
#             np.linalg.norm(np.array(t) - np.array(median_tuple)) for t in coordinates_tuples
#         ]
#         # Find the index of the tuple with the maximum distance
#         farthest_index = max(enumerate(distances_tuples), key=lambda x: x[1])[0]
#         farthest_index = distances_tuples.index(max(distances_tuples))


#         # Optimize the route using the distance matrix and farthest point index as the starting point
#         best_route = optimize_routes(distances,0,1)
#         # Save the best route to a CSV file with the city name in the output folder
#         df_city.iloc[best_route][:-1].reset_index(drop=True).to_csv(
#             f"data/output/{city}_routing.csv"
#         )
        

#         # # Plot the best route on the map for the city "Ulldecona" (first city in the iteration)
#         # if city == "Tangerang Selatan":
#         #     df_best_route = df_city.iloc[best_route]
#         #     coordinates = list(zip(df_best_route["lat"], df_best_route["lng"]))
#         #     my_map = plot_route(coordinates, dist=2000)
#         #     # saving interactive map in html
#         #     my_map.save('maps/route'+city+'.html')
#         dictResult = {"places":list(df_city.name)}
#         dictResult["coordinates"] = coordinates
#         dictResult["distance"] = distances_tuples
#         dictResult["result"] = df_city.name[best_route].reset_index(drop=True).tolist()
#     return dictResult
   