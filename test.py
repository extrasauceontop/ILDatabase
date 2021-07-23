import requests
import pandas as pd
import os
from datetime import date

final_year = date.today().year

# Searching by iterating over years, because that seemed easiest
search_year = 1900
while True:
    print("")
    print("")
    print(search_year)
    breaker = 0
    while True:
        try:
            response = requests.get("https://ilthermo.boulder.nist.gov/ILT2/ilsearch?cmp=&ncmp=0&year=" + str(search_year) + "&auth=&keyw=&prp=0", timeout=180).json()
            break
        except Exception:
            breaker = breaker+1
            if breaker == 10:
                print("DEAD")
                raise Exception
            continue
        
    print(len(response["res"]))
    for item in response["res"]:
        
        # Creating the folder
        breaker = 0
        while True:
            try:
                item_data = requests.get("https://ilthermo.boulder.nist.gov/ILT2/ilset?set=" + item[0]).json()
                break
            except Exception:
                breaker = breaker+1
                if breaker == 10:
                    print("DEAD")
                    raise Exception
                continue

        folder_name = ""
        for component in item_data["components"]:
            folder_name = component["name"] + "--"
        
        folder_name = (folder_name + item[2]).replace(" ", "--").replace(",", "---").replace(".", "----").replace(":", ";").replace("/", "-divide-")

        # In the event the file already exists, add a number to the filename
        y = 0
        while True:
            try:
                os.mkdir("data/" + folder_name)
                file_name = "data/" + folder_name
                break
            except Exception:
                try:
                    os.mkdir("data/" + folder_name + "(" + str(y) + ")")
                    file_name = "data/" + folder_name + "(" + str(y) + ")"
                    break
                except Exception:
                    y = y+1
                    if y == 1000000:
                        print("BROKEN FILE")
                        raise Exception

        # Making the csv files, 2 per paper. info.csv and data.csv
        # Info file creation here
        info_dict = {}
        z = 0
        for component in item_data["components"]:
            z = z+1
            for key in component.keys():
                if key == "name" or key == "sample":
                    continue
                info_dict[key + "_" + component["name"]] = [component[key]]
        
        info_dict["reference"] = [item[1]]
        info_dict["property"] =  [item[2]]
        info_dict["phases"] =  [item[3]]
        info_dict["Datapoints"] = [item[7]]

        info_df = pd.DataFrame(info_dict)
        info_df.to_csv(file_name + "/info.csv", index=False)

        # Data file creation here
        data_keys = []
        for header in item_data["dhead"]:
            try:
                if header[1] is not None:
                    data_keys.append(header[0] + "-" + header[1])
                else:
                    data_keys.append(header[0])
            
            except Exception:
                data_keys.append(header[0])

        data_list = []
        for row in item_data["data"]:
            data_dict = {}

            count = 0
            try:
                for header in data_keys:

                    data_values = row[count]
                    final_value = ""
                    for value in data_values:
                        final_value = final_value + value + "+-"
                    
                    final_value = final_value[:-2]
                    data_dict[header] = final_value

                    count = count+1
            
            except Exception:
                continue
            
            data_list.append(data_dict)
                
        data_df = pd.DataFrame(data_list)
        data_df.to_csv(file_name + "/data.csv", index=False)
    
    search_year = search_year + 1
    if search_year > final_year:
        break