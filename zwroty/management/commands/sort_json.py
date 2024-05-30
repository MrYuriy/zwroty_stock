import json

def sort_sku_path(input_file_path: str)-> str:
    """
        sort json file by sku_log return path to sorted file
    """
    input_file_path = "sku_barcode.json"
    output_file_path = "sorted_sku_barcode.json"

    # Read the data from the input JSON file
    with open(input_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)["items"]

    # Sort the data based on 'sku_handl' or fallback to 'sku_log'
    sorted_data = sorted(data, key=lambda x: x["sku_log"])

    # Write the sorted data to a new JSON file
    with open(output_file_path, "w", encoding="utf-8") as file:
        json.dump({"items": sorted_data}, file, ensure_ascii=False, indent=2)

    print(f"Sorted data has been written to {output_file_path}")
    return output_file_path
