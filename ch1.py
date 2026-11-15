# from abc import ABC, abstractmethod
#
#
# # Банкомат.
# # Инициализируется набором купюр и умеет выдавать купюры для заданной суммы, либо отвечать отказом.
# # При выдаче купюры списываются с баланса банкомата.
# # Допустимые номиналы: 50₽, 100₽, 500₽, 1000₽, 5000₽.
# class ATM:
#     pass  # место для кода
#
#
# # API для взаимодействия с аппаратурой банкомата.
# # Краткий ликбез по устройству банкомата:
# # - деньги располагаются в кассетах, кассеты устанавливаются инкассатором;
# # - в каждой кассете лежат свои купюры, количество известно инкассатору при установке;
# # - банкомат может подсчитать оставшиеся в кассетах банкноты, но эта операция занимает около 10 секунд,
# #   и шумная, её стоит вызывать как можно реже.
# class SDK(ABC):
#
#     @abstractmethod
#     def count_banknotes(self, banknote: int) -> int:
#         """Вернуть количество банкнот заданного номинала, оставшихся в кассетах."""
#         pass
#
#     @abstractmethod
#     def move_banknote_to_dispenser(self, banknote: int, count: int) -> None:
#         """
#         Переместить указанное число банкнот заданного номинала из кассет в диспенсер.
#         Вызывается при подготовке купюр к выдаче.
#         """
#         pass
#
#     @abstractmethod
#     def open_dispenser(self) -> None:
#         """Открыть диспенсер и выдать подготовленные купюры пользователю."""
#         pass

from abc import ABC, abstractmethod


class ATM:
    DENOMINATIONS = (5000, 1000, 500, 100, 50)

    def __init__(self, sdk: "SDK") -> None:
        self._sdk = sdk
        self._stock = {
            denom: self._sdk.count_banknotes(denom)
            for denom in self.DENOMINATIONS
        }

    def withdraw(self, amount: int) -> bool:
        if amount <= 0 or amount % self.DENOMINATIONS[-1] != 0:
            return False

        plan = self._make_plan(amount)
        if plan is None:
            return False

        for denom, count in plan.items():
            self._sdk.move_banknote_to_dispenser(denom, count)
        self._sdk.open_dispenser()

        for denom, count in plan.items():
            self._stock[denom] -= count

        return True

    def _make_plan(self, amount: int):
        plan = {}
        remaining = amount

        for denom in self.DENOMINATIONS:
            if remaining < denom:
                continue
            take = min(self._stock[denom], remaining // denom)
            if take > 0:
                plan[denom] = take
                remaining -= take * denom
            if remaining == 0:
                break

        return plan if remaining == 0 else None


class SDK(ABC):

    @abstractmethod
    def count_banknotes(self, banknote: int) -> int:
        """Вернуть количество банкнот заданного номинала, оставшихся в кассетах."""
        pass

    @abstractmethod
    def move_banknote_to_dispenser(self, banknote: int, count: int) -> None:
        """
        Переместить указанное число банкнот заданного номинала из кассет в диспенсер.
        Вызывается при подготовке купюр к выдаче.
        """
        pass

    @abstractmethod
    def open_dispenser(self) -> None:
        """Открыть диспенсер и выдать подготовленные купюры пользователю."""
        pass


class FakeSDK(SDK):
    def __init__(self, stock):
        self.stock = dict(stock)
        self.moves = []
        self.opened = False

    def count_banknotes(self, banknote):
        return self.stock.get(banknote, 0)

    def move_banknote_to_dispenser(self, banknote, count):
        assert count <= self.stock[banknote], "нельзя выдать больше, чем есть"
        self.moves.append((banknote, count))

    def open_dispenser(self):
        self.opened = True



