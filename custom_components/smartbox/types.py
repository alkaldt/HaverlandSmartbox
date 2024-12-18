from typing import Dict, Union

FactoryOptionsDict = Dict[str, bool]

SetupDict = Dict[str, Union[bool, float, str, FactoryOptionsDict]]

StatusDict = Dict[str, Union[bool, int, float, str]]

SamplesDict = Dict[str, Union[bool, int, float, str]]
