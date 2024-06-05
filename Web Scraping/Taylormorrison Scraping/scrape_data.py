import re
import logging
import requests
import json
import psutil
from time import time
import pandas as pd
from bs4 import BeautifulSoup

logging.basicConfig(
    filename="scrape_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

SITE_URL = "https://www.taylormorrison.com"
STATE_CODE = "az"
STATE = "Arizona"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

# Using connection pool for potentially faster requests
session = requests.Session()
session.adapters["http://"] = requests.adapters.HTTPAdapter(pool_connections=10)
session.adapters["https://"] = requests.adapters.HTTPAdapter(pool_connections=10)


def scrape_data():
    # Using this url to get the page and extarcting script containing community and avialable homes data.
    url = f"{SITE_URL}/{STATE_CODE}#t=Communities"

    response = session.get(url=url, headers=HEADERS)

    if response.status_code != 200:
        raise Exception(
            f"{response.status_code}, Problem fetching respose from url {url}"
        )

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the script that contains the JSON data
    script_tag = soup.find(
        "script", string=re.compile(r"window\.TM\.client\.scDataStore\.data")
    )

    # Convert Script to string
    script_content = script_tag.string

    # Extracting the JSON part from the JavaScript
    json_data_match = re.search(
        r"window\.TM\.client\.scDataStore\.data\s*=\s*(\{.*?\});",
        script_content,
        re.DOTALL,
    )

    json_data_str = json_data_match.group(1)

    data = json.loads(json_data_str)

    # Get Communities and Available Home Data in separate variable
    communities_search_results = move_in_ready_search_results = None
    for key in data:
        if (
            "communitiesSearchResults" in data[key]
            and "moveInReadySearchResults" in data[key]
        ):
            communities_search_results = data[key]["communitiesSearchResults"]
            move_in_ready_search_results = data[key]["moveInReadySearchResults"]
            break

    get_community_data(communities_search_results)
    get_available_homes_data(move_in_ready_search_results)


def get_community_data(communities_search_results):
    communities_data = []
    for community_group in communities_search_results["results"]:
        if "communityGroupData" in community_group:
            for communities in community_group["communityGroupData"][
                "communitiesArray"
            ]:
                community_data = communities["communityData"]
                format_data(community_data, communities_data)
        elif "communityData" in community_group:
            community_data = community_group["communityData"]
            format_data(community_data, communities_data)

    # Convert the List to Dataframe
    df = pd.DataFrame(communities_data)

    # Replace null or NaN with "N/A"
    df = df.fillna("N/A")

    # Store in CSV file
    df.to_csv("Community_Data.csv", index=False)


def format_data(community_data, communities_data):
    community_page_url = f"{SITE_URL}{community_data['communityDetailLink']['Url']}"
    address = get_address_from_community_page(community_page_url)
    communities_data.append(
        {
            "State": STATE_CODE,
            "Name": community_data["communityName"],
            "Notes": community_data["communityStatus"],
            "Latitude": community_data["latLng"]["lat"],
            "Longitude": community_data["latLng"]["lng"],
            "Address": address if address else "N/A",
            "Pricing": community_data["price"],
            "Area": f"{community_data['minSqFt']} - {community_data['maxSqFt']}",
            "URL": community_page_url,
        }
    )


def get_address_from_community_page(url):
    response = session.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    scripts = soup.find_all("script", type="text/template")

    for script in scripts:
        script_data = script.text.strip()
        try:
            data = json.loads(script_data)
            if (
                "contact" in data
                and "salesCenter" in data["contact"]
                and "address" in data["contact"]["salesCenter"]
            ):
                address = data["contact"]["salesCenter"]["address"]
                return f"{address['address']}, {address['city']}, {address['state']} {address['zip']}"
        except (json.JSONDecodeError, KeyError):
            pass

    return None


def get_available_homes_data(move_in_ready_search_results):
    move_in_ready_homes_data = []
    for community_data in move_in_ready_search_results["results"]:
        if "communityData" in community_data:
            community_name = community_data["communityData"]["communityName"]
            community_state = community_data["communityData"]["communityState"]
            for move_in_ready_homes in community_data["communityData"][
                "moveInReadyHomesDataArray"
            ]:
                move_in_ready_home = move_in_ready_homes["moveInReadyHomeData"]

                price = move_in_ready_home["price"]
                old_price = (
                    move_in_ready_home["wasPrice"]
                    if move_in_ready_home["wasPrice"]
                    else price
                )
                discount_price = old_price - price

                move_in_ready_homes_data.append(
                    {
                        "Region": STATE_CODE,
                        "Community_Name": community_name,
                        "Plan": move_in_ready_home["floorPlan"],
                        "Location": f"{move_in_ready_home['city']}, {community_state}",
                        "Postal_Code": move_in_ready_home["zip"],
                        "Estimated_Completion_Date": (
                            move_in_ready_home["readyDate"]
                            if move_in_ready_home["readyDate"]
                            else "N/A"
                        ),
                        "Price": old_price,
                        "Discount": discount_price,
                        "Final_Price": price,
                        "Address": move_in_ready_home["address"],
                        "Latitude": move_in_ready_home["lat"],
                        "Longitude": move_in_ready_home["lng"],
                        "Area": move_in_ready_home["sqft"],
                        "Beds": move_in_ready_home["bed"],
                        "Baths": move_in_ready_home["fullBath"],
                        "Garages": move_in_ready_home["garage"],
                        "Stories": get_story(move_in_ready_home),
                        "URL": f"{SITE_URL}{move_in_ready_home['homeDetailLink']['Url']}",
                    }
                )

    # Convert the List to Dataframe
    df = pd.DataFrame(move_in_ready_homes_data)

    # Replace null or NaN with "N/A"
    df = df.fillna("N/A")

    # Store in CSV file
    df.to_csv("Available_Homes_Data.csv", index=False)


def get_story(move_in_ready_home):
    if move_in_ready_home["isSingleStory"]:
        story = 1
    elif move_in_ready_home["isSecondStory"]:
        story = 2
    elif move_in_ready_home["hasThirdStory"]:
        story = 3
    else:
        story = "N/A"

    return story


def main():
    try:
        scrape_data()

        print("Scarped Data Successfully!")
    except Exception as e:
        logging.error(f"Error: {str(e)}")


# Function to get memory usage
def get_memory_usage():
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)  # Memory usage in MB


# Function to measure time taken by the script
def measure_time(func):
    start_time = time()
    func()
    end_time = time()
    return end_time - start_time  # Time in seconds


if __name__ == "__main__":
    memory_before = get_memory_usage()
    time_taken = measure_time(lambda: main())
    memory_after = get_memory_usage()

    print(f"Memory Before Execution: {memory_before:.2f} MB")
    print(f"Memory After Execution: {memory_after:.2f} MB")
    print(f"Memory Used: {memory_after - memory_before:.2f} MB")
    print(f"Time Taken: {time_taken:.2f} seconds")
