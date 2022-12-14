import argparse
import json
import logging
from operator import mul, truediv
import sys

CONVERSION_TABLE = {
    "kWh2Wh": {"operator": "*", "factor": 1000},
    "kWh2KJ": {"operator": "*", "factor": 3600},
    "kWh2J": {"operator": "*", "factor": 3600000},
    "Wh2kWh": {"operator": "/", "factor": 1000},
    "Wh2KJ": {"operator": "*", "factor": 3.6},
    "Wh2J": {"operator": "*", "factor": 3600},
    "KJ2kWh": {"operator": "/", "factor": 3600},
    "KJ2Wh": {"operator": "/", "factor": 3.6},
    "KJ2J": {"operator": "*", "factor": 1000},
    "J2kWh": {"operator": "/", "factor": 3600000},
    "J2Wh": {"operator": "/", "factor": 3600},
    "J2KJ": {"operator": "/", "factor": 1000},
}


class EnergyProfileConverter:
    def __init__(self):
        self.parse_commandline_arguments()
        self.initialize()

    def initialize(self):
        # setup logging
        self.setup_logging(self.args["debug"])

        self.load_json_data(self.args["in"])
        self.output_dict = self.initialize_output_dict(self.original_data)

        self.start_interval = int(self.original_data["interval_in_minutes"])
        self.convert_interval = int(self.args["interval"])

        self.from_unit = self.original_data["unit"]
        self.to_unit = self.args["unit"]

        self.calculate_window_size_and_padding(
            self.start_interval, self.convert_interval
        )

        # read the conversion operator and factor once as it is static for all
        # conversion operations
        conversionkey = self.from_unit + "2" + self.to_unit
        self.conversion_operator = CONVERSION_TABLE[conversionkey]["operator"]
        self.conversion_factor = CONVERSION_TABLE[conversionkey]["factor"]

    def setup_logging(self, debug):
        if debug:
            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        else:
            logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    def parse_commandline_arguments(self):
        parser = argparse.ArgumentParser()

        parser._action_groups.pop()
        required = parser.add_argument_group("required arguments")
        optional = parser.add_argument_group("optional arguments")

        # use if -in and -out need to be positional arguments
        # add validation for positional arguments if needed
        # required.add_argument("in",
        #     nargs="?",
        #     help="Path of source file to read from")
        # required.add_argument("out",
        #     nargs="?",
        #     help="Path of destination file to write converted data to")

        required.add_argument(
            "-in", help="Path of source file to read from", required=True
        )

        required.add_argument(
            "-out",
            help="Path of destination file to write converted data to",
            required=True,
        )

        required.add_argument(
            "-interval",
            choices=[1, 5, 15, 30, 60, 1440],
            type=int,
            help="Convert to interval in minutes",
            required=True,
        )

        required.add_argument(
            "-unit",
            choices=["kWh", "Wh", "KJ", "J"],
            help="Convert data values to target unit",
            required=True,
        )

        optional.add_argument(
            "--debug", action="store_true", help="Print debug messages to stderr"
        )

        # convert args to dict
        self.args = vars(parser.parse_args())

    def load_json_data(self, filename):
        logging.info(f"will read JSON from {filename} ..")

        with open(filename) as f:
            self.original_data = json.load(f)

    def write_json_data(self, filename):
        logging.info(f"will write output JSON to {filename}")

        with open(filename, "w") as f:
            json.dump(self.output_dict, f, indent=4)

    def initialize_output_dict(self, original_data):
        logging.info("will initialize output JSON data structure ..")

        output_dict = dict()
        # duplicate header information
        for key in original_data:
            # initialize new empty data array
            if key == "data":
                output_dict[key] = []
                continue

            output_dict[key] = original_data[key]

        output_dict["interval_in_minutes"] = self.args["interval"]
        output_dict["unit"] = self.args["unit"]

        return output_dict

    def get_elements_from_sliding_window(self, data_array, window_size):
        """
        get_elements_from_sliding_window iterates over the data_array and yields
        an iterable generator which can be used to iterate over the data_array.

        Parameters:
            data_array  .. array of data to iterate over
            window_size .. count of items which should be returned for every iteration

        Returns:
            yield iterable generator
        """
        if len(data_array) < window_size:
            logging.error("error, window size bigger than data array")
            return None

        window_position = 0
        while window_position < len(data_array):
            yield data_array[window_position : window_position + window_size]
            window_position += window_size

    def calculate_window_size_and_padding(self, start_interval, convert_interval):
        """
        calculate_window_size_and_padding is used to determine the window size
        and the padding.

        The window size will be used to iterate over the data array. If the
        conversion is from larger to smaller the window will always be 1.
        If the conversion is from smaller to larger the window size needs to be
        calculated. In this case no padding is needed.
        The padding will be used to fill the dataset when converting from
        larger to smaller.

        Parameters:
            start_interval   .. interval in minutes given by the in-file
            convert_interval .. interval in minutes to change to

        Returns:
            Noting
        """
        # if we convert from larger to smaller the window will always be 1
        # if we convert from smaller to larger we will calculate the size next
        self.window_size = 1

        # padding is only needed if we convert from larger to smaller
        self.padding = 0

        # calculate window_size or padding
        if start_interval < convert_interval:
            self.window_size = int(convert_interval / start_interval)
            logging.debug(f"Window size: {self.window_size}")
        else:
            self.padding = int(start_interval / convert_interval)
            logging.debug(f"Padding size: {self.padding}")

    def convert_unit(self, value):
        """
        convert_unit converts a value to the unit provided as a CLI parameter.
        To determine with which factor and with which operator to convert the
        value a CONVERSION_TABLE is used.

        Parameter:
            value .. parameter to be converted

        Returns:
            Converted value
        """
        if self.from_unit == self.to_unit:
            logging.info(
                f"units from {self.from_unit} to {self.to_unit} are equal, will not convert .."
            )
            return value

        logging.debug(
            f"will convert value {value} from {self.from_unit} to {self.to_unit} .."
        )

        # move conversion operator and factor initialization to class init
        # as those values are static for all operations
        # conversionkey = self.from_unit + "2" + self.to_unit
        # operator = CONVERSION_TABLE[conversionkey]["operator"]
        # factor = CONVERSION_TABLE[conversionkey]["factor"]

        if self.conversion_operator == "/":
            return truediv(value, self.conversion_factor)
        elif self.conversion_operator == "*":
            return mul(value, self.conversion_factor)
        else:
            logging.error(
                f"ERROR: unknown operator {self.conversion_operator} found in conversion table"
            )
            return None

    def convert(self):
        """
        convert is the main entrypoint of the epc class. It iterates over the
        data array, calculates the values, converts values and stores the
        results in the output dict and writes the new JSON object to the outfile.

        Parameters:
            None

        Returns:
            None
        """
        # iterate directly
        # window_position = 0
        # while True:
        #     print(f"will get elements from {window_position} to {window_position+window_size}")
        #     elements = data["data"][window_position:window_position+window_size]
        #     print(elements)
        #     window_position += window_size
        #     if len(elements) != window_size:
        #         break

        # slide a window with window_size length over the array to extract those elements
        # use yield to implement iterating with a sliding window
        for window_elements in self.get_elements_from_sliding_window(
            self.original_data["data"], self.window_size
        ):
            # build the average
            if self.start_interval < self.convert_interval:
                average = sum(window_elements) / self.window_size
                converted_average = self.convert_unit(average)
                logging.debug(
                    f"converted unit from {average}{self.from_unit} to {converted_average}{self.to_unit}"
                )
                self.output_dict["data"].append(converted_average)
            else:
                # add n elements same as current element
                single_element = self.convert_unit(window_elements[0])
                logging.debug(
                    f"converted unit from {window_elements[0]}{self.from_unit} to {single_element}{self.to_unit}"
                )

                self.output_dict["data"].extend(
                    [single_element for v in range(0, self.padding)]
                )

        self.write_json_data(self.args["out"])


if __name__ == "__main__":
    epc = EnergyProfileConverter()
    epc.convert()
