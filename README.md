# Energy Profile Converter

Compensation work for SWD - Software Development I

## Introduction

The goal of this project is to create a python program that can read energy profiles and perform operations on them.

### Energy profile

An energy profile is a JSON file describing the generated or consumed power of any system over a year. For example a file could describe how much energy was generated by a solar tracker (like the one in front of the FH JOANNEUM in Kapfenberg) over a year.

#### Format

An energy profile looks like this:

```
{
    "name": "Solar Tracker",
    "interval_in_minutes": "15",
    "unit": "kWh",
    "data": [0.0,0.0,0.1,...]
}
```

| JSON Field          | Description                                                                                            |
|---------------------|--------------------------------------------------------------------------------------------------------|
| name                | name of the system                                                                                     |
| interval_in_minutes | interval of data. For example, 15 means there is a data entry for every 15 minutes (35040 for a year). |
| unit                | the unit of the data.                                                                                  |
| data                | array with the data itself.                                                                            |

For the example above this means: The data is an array with 35040 values. Each value describes the generated energy for the next 15 minutes in kWh.

## Usage

The script can be run like this:

```
$ python epc.py -in data/example.json -out data/output.json -interval 15 -unit Wh
```

The following command line parameters are required:

| Parameter | Description                                                                                   |
|-----------|-----------------------------------------------------------------------------------------------|
| -in       | Input filename                                                                                |
| -out      | Output filename                                                                               |
| -interval | Interval the data should be converted to in minutes<br>Allowed values: 1, 5, 15, 30, 60, 1440 |
| -unit     | Unit the data should be converted to<br>Allowed values: kWh, Wh, KJ, J                        |

After all data has been converted, the result will be written to the output filename in JSON notation.

## Dependencies

Only the Python 3.10 standard library is used, no further dependencies.
