"""Type for smartbox."""

FactoryOptionsDict = dict[str, bool]

SetupDict = dict[str, bool | float | str | FactoryOptionsDict]

StatusDict = dict[str, bool | int | float | str]

SamplesDict = dict[str, bool | int | float | str]
