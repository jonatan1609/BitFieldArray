import typing
from collections import UserList
from typing import overload

__all__ = ['BitField', 'BitFieldArray']


class BitField:
    """
    This class represents a bitfield in the array, it consists of {value: maximum_bits}.
    If you try to assign a value which is larger than the maximum allowed bits for a particular bitfield,
    it gets masked and only keeps the first bits which doesn't exceed the maximum amount of bits.

    Parameters:
        max_bits: maximum of bits for a particular bitfield.
    """

    def __init__(self, max_bits):
        self._value = None
        self.max_bits = max_bits

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = self.mask(value, self.max_bits)

    @staticmethod
    def mask(value, bits: int):
        return value & ((1 << bits) - 1)

    @property
    def is_null(self):
        """Determines whether the value has content in it or not."""
        return self.value is None

    def assign(self, value):
        """This method assigns value to the particular bit"""
        self.value = value

    @staticmethod
    def repr_as_binary(value):
        """This method returns the binary representation of the particular value"""
        b = bin(value)[2:]
        return b.zfill(len(b) + -len(b) % 8)

    def __repr__(self):
        return f"{self.repr_as_binary(self._value or 0)}: {self.max_bits}"

    __str__ = __repr__


_bits_sentinel = BitField(0)


class BitFieldArray(UserList):
    """This class represents an array of bit fields,
    each bit field contains a value and a maximum amount of bits to take in the array.

    Parameters:
        *fields: A Tuple of `int`. Determines the bits distribution in the array.
    """
    def __init__(self, *fields):
        super().__init__(map(BitField, fields))

    @overload
    def assign(self, value: int):
        pass

    @overload
    def assign(self, values: typing.Iterable[int]):
        pass

    def assign(self, value):
        """You can use this function to assign bitfields into the array.
        This function can accept either a single value which will be assigned to the first empty bitfield,
        or a sequence of values which will be assigned one by one to the first empty bitfield and farther.

        Parameters:
            value: Either a single value or a sequence of values.
        """
        generator = (bits for bits in self.data if bits.is_null)
        if isinstance(value, int):
            series_of_bits = next(generator, _bits_sentinel)
            series_of_bits.assign(value)
        elif isinstance(value, typing.Iterable):
            for value, bits in zip(value, generator):
                bits.assign(value)
        return self

    def __str__(self):
        return f"<BitFieldArray {super().__str__()}>"

    def delete(self, index):
        """Delete a bitfield from the array.
        Parameters:
            index: `int`, the index of the bitfield to be deleted.
        """
        del self.data[index]

    def export(self):
        """Export the array as an integer, which can be used later to access index.
        You can access any index by
        (array >> SHIFT_RIGHT_X_BITS) & ((1 << BITS) - 1)
        for example:
            array = BitFieldArray(3, 7, 8, 9)
            array.assign([5, 6, 7, 8])
            number = array.export()
            print((number >> 0) & ((1 << 3) -1)) # 5
            print((number >> 3) & ((1 << 7) -1)) # 6
            print((number >> 10) & ((1 << 8) -1)) # 7
            print((number >> 18) & ((1 << 9) -1)) # 8

            0 is the first time we access the array, we don't need to shift it.
            And then we shift is 3 bits since the last one was 3 bits.
            And then we shift it 10 bits since the latter ones were 3+7 bits, and so on.
            The goal is to shift away the values before the particular value we need so it will be the first value
            that we need to access.
            You can use >>= every time and then you don't need to sum the former values' bits as in 3+7.

            number = array.export()
            for i in (3, 7, 8, 9): # bits in the structure
                print(number & (1 << i) -1)
                number >>= i

            And eventually the number will be 0 - consumed array.
        """
        n = 0
        pushed = 0
        for i in self.data:
            if i.is_null:
                break
            n |= i.value << pushed
            pushed += i.max_bits
        return n

    def export_as_bytes(self, order):
        """Export the array as bytes.
        To send it over the network, for example.

        Parameters:
            order: the endianness of the bytes. Must be either 'little' or 'big'.
                    You can use the native order - sys.byteorder.
        """
        data = self.export()
        return data.to_bytes((data.bit_length() + 7) // 8, order)

    def to_list(self):
        """Returns the array as a list of the values in the array."""
        return [bits.value for bits in self.data]

    def from_int(self, value: int):
        """Instead of manually accessing indexes with the resulting number of `array.export()`, you can create an instance
            of the array which specifies the bits distribution and then call this method with the number.
        For example:
            # 7 boolean flags, the first and last are True and the rest are False.
            flags = BitFieldArray(1, 1, 1, 1, 1, 1, 1)
            flags.from_int(62)
            print(flags.to_list())

        Results in [0, 1, 1, 1, 1, 1, 0].

        Parameters:
            value: `int`, the number to create the instance from.
        """
        data = []
        for bits in self.data:
            data.append(value & (1 << bits.max_bits) - 1)
            value >>= bits.max_bits
        return self.assign(data)

    def from_bytes(self, value: bytes, order: str):
        """The same as BitFieldArray.from_int but for bytes. Usually used when you send array over the network.
        Parameters:
            value: `bytes`. The bytes to create the instance from.
            order: `str`, the endianness of the bytes. Must be either 'little' or 'big'.
                    You can use the native order - sys.byteorder.
        """
        as_int = int.from_bytes(value, order)
        return self.from_int(as_int)
