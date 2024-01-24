from abc import ABC, abstractproperty


class TreasuryService(ABC):
    @abstractproperty
    def UST30Y(self) -> float:
        pass

    @abstractproperty
    def UST10Y(self) -> float:
        pass

    @abstractproperty
    def UST5Y(self) -> float:
        pass

    @abstractproperty
    def UST1Y(self) -> float:
        pass

    @abstractproperty
    def UST6MO(self) -> float:
        pass

    @abstractproperty
    def UST3MO(self) -> float:
        pass

    @abstractproperty
    def UST1MO(self) -> float:
        pass
