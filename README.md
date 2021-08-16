# BitFieldArray
#### This kind of thing is useful when you want to transmit/receive arrays and structs over the network, and more. For example, you can turn the array `[False, True, True, True, True, True, False]` into the number 62 and then you can access it with bitwise operators or with this module.
> `class BitFieldArray`

This class represents an array of bit fields,
each bit field contains a value and a maximum amount of bits to take in the array.

**Parameters**:
    
> *fields: A Tuple of `int`. Determines the bits distribution in the array.

### Methods:
```python
def assign(self, values: typing.Iterable[int]):
```
```python
def assign(self, value: int):
```

+ You can use this function to assign bitfields into the array.
This function can accept either a single value which will be assigned to the first empty bitfield,
or a sequence of values which will be assigned one by one to the first empty bitfield and farther.

**Parameters**:
> value: Either a single value or a sequence of values.

-----
```python
def delete(self, index):
```
+ Delete a bitfield from the array.

**Parameters:**
>index: `int`, the index of the bitfield to be deleted.
---
```python
def export(self):
```
+ Export the array as an integer, which can be used later to access index.
You can access any index by
`(array >> SHIFT_RIGHT_X_BITS) & ((1 << BITS) - 1)`
for example:
```python
array = BitFieldArray(3, 7, 8, 9)
array.assign([5, 6, 7, 8])
number = array.export()
print((number >> 0) & ((1 << 3) -1)) # 5
print((number >> 3) & ((1 << 7) -1)) # 6
print((number >> 10) & ((1 << 8) -1)) # 7
print((number >> 18) & ((1 << 9) -1)) # 8
```
0 is the first time we access the array, we don't need to shift it.

And then we shift it 3 bits since the last one was 3 bits.

And then we shift it 10 bits since the latter ones were 3+7 bits, and so on.

The goal is to shift away the values before the particular value we need so it will be the first value
that we need to access.
You can use `>>=` every time and then you don't need to sum the former values' bits as in 3+7.

```python
number = array.export()
for i in (3, 7, 8, 9): # bits in the structure
    print(number & (1 << i) -1)
    number >>= i
```
And eventually the number will be 0 - consumed array.

---
```python
def export_as_bytes(self, order):
```
+ Export the array as bytes. To send it over the network, for example.

**Parameters:**
> order: the endianness of the bytes. Must be either 'little' or 'big'. You can use the native order - `sys.byteorder`.
---
```python
def to_list(self):
```
+ Returns the array as a list of the values in the array.
---
```python
def from_int(self, value: int):
```
+ Instead of manually accessing indexes with the resulting number of `array.export()`, you can create an instance of the array which specifies the bits distribution and then call this method with the number.

For example:
```python
# 7 boolean flags, the first and last are True and the rest are False.
flags = BitFieldArray(1, 1, 1, 1, 1, 1, 1)
flags.from_int(62)
print(flags.to_list())
```
Results in `[0, 1, 1, 1, 1, 1, 0]`.

**Parameters**:
> value: `int`, the number to create the instance from.
---
```python
def from_bytes(self, value: bytes, order: str):
```
+ The same as BitFieldArray.from_int but for bytes. Usually used when you send array over the network.
> value: `bytes`. The bytes to create the instance from.

> order: `str`, the endianness of the bytes. Must be either 'little' or 'big'. You can use the native order - sys.byteorder.

---

## examples
```python
from BitFieldArray import BitFieldArray

array = BitFieldArray(1, 1, 1, 1)
array.assign(False)
array.assign(False)
array.assign([True, True])

print(array)
print(array.export())
```
will return `<BitFieldArray [00000000: 1, 00000000: 1, 00000001: 1, 00000001: 1]>`, and `export`ing it will return 12.

---
```python
from BitFieldArray import BitFieldArray

array = BitFieldArray(30, 16, 16, 2) # 64 bit array, 8 byte.
array.assign([999888777, 12345, 56789, 3])
print(array)
print(array.export())
```
it will print out
`<BitFieldArray [00111011100110010001011110001001: 30, 0011000000111001: 16, 1101110111010101: 16, 00000011: 2]>` and then `17831241924730230665`.

The number 17831241924730230665 is the array itself, and it can be accessed with bitwise operators as explained under the method `export`.

It can also be used with `from_int`.

---

```python
from BitFieldArray import BitFieldArray
from sys import byteorder

array = BitFieldArray(10, 10, 10, 10, 12, 12, 12, 12) # 88 bit array
array.assign([550, 600, 650, 700, 1000, 2000, 3000, 4000])
print(array.export_as_bytes(byteorder))
```
will result in `b'&b\xa9(\xaf\xe8\x03}\xb8\x0b\xfa'`. And then you can do

```python
from BitFieldArray import BitFieldArray
from sys import byteorder

array = BitFieldArray(10, 10, 10, 10, 12, 12, 12, 12) # 88 bit array
obj = array.from_bytes(b'&b\xa9(\xaf\xe8\x03}\xb8\x0b\xfa', byteorder)
print(obj)
print(obj.to_list())
```

