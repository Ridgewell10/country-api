import requests

BASE = "http://127.0.0.1:5000/"

data = [{"country_name": "Afghanistan", "alpha_2_code": "AF", "alpha_3_code": "AFG", "currencies": "AFN"},
    {"country_name": "Argentina", "alpha_2_code": "AR", "alpha_3_code": "ARG", "currencies": "ARS"},
    {"country_name": "Brazil", "alpha_2_code": "BR", "alpha_3_code": "BRA", "currencies": "BRL"}]

for i in range(len(data)):
    response = requests.put(BASE + "country/" + str(i), data[i])
    print(response.json())

input()
response = requests.get(BASE + "country/2", {})
print(response.json())

#response = requests.patch(BASE + "country/1", {"alpha_3_code": "BRR"})
#print(response.json())