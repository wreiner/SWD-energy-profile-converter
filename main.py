import json


def get_elements_from_sliding_window(data_array, window_size):
    """
    get_elements_from_sliding_window reads
    """
    if len(data_array) < window_size:
        print("error, window size bigger than data array")
        return None

    window_position = 0
    while window_position < len(data_array):
        yield data_array[window_position:window_position+window_size]
        window_position += window_size


def main():
    with open('data/15min-test-int.json', 'r') as f:
        data = json.load(f)

    start_interval = int(data["interval_in_minutes"])
    convert_interval = 60

    # if we convert from larger to smaller the window will always be 1
    # if we convert from smaller to larger we will calculate the size next
    window_size = 1

    # padding is only needed if we convert from larger to smaller
    padding = 0

    # calculate window_size or padding
    if start_interval < convert_interval:
        window_size = int(convert_interval/start_interval)
        print(f"Window size: {window_size}")
    else:
        padding = int(start_interval/convert_interval)
        print(f"Padding size: {padding}")

    # print(data["data"])

    # slide a window with window_size length over the array to extract those elements
    # use yield to implement iterating with a sliding window
    for window_elements in get_elements_from_sliding_window(data["data"], window_size):
        print(window_elements)
        # build the average
        if start_interval < convert_interval:
            print(sum(window_elements) / window_size)
        else:
            # add n elements same as current element
            pass

    # iterate directly
    # window_position = 0
    # while True:
    #     print(f"will get elements from {window_position} to {window_position+window_size}")
    #     elements = data["data"][window_position:window_position+window_size]
    #     print(elements)
    #     window_position += window_size
    #     if len(elements) != window_size:
    #         break



    # 1 minute
    # 15 minutes
    # 30 minutes
    # 1 hour
    # 1 day

if __name__ == "__main__":
    main()