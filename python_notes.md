# Python

TODO: Walrus operator <https://realpython.com/python-walrus-operator/>

TODO: loguru vs logging

TODO: argparse <https://docs.python.org/3/library/argparse.html>, xargs

TODO: managed attribute (setter)


* - unpacking operator, unpacks to a tuple
=> *args unpacks args into a (immutable) tuple
```python
def my_sum(*args):
    result = 0
    # Iterating over the Python args tuple
    for x in args:
        result += x
    return result
```

**kwargs - unpacks dictionary 

```python
def concatenate(**kwargs):
    result = ""
    # Iterating over the Python kwargs dictionary
    for arg in kwargs.values():
        result += arg
    return result

print(concatenate(a="Real", b="Python", c="Is", d="Great", e="!"))
```

Remember to loop over kwargs.values(), else it will loop over keys 

Use underscore as commas in large numbers: ```10_000```

```python
>>> for index, fruit in enumerate(fruits):
...     print(index, fruit)
...
0 orange
1 apple
2 mango
3 lemon
```

Zip enumerates multiple iterables simultaneously - WILL FAIL IF ANY ITERABLES ARE EMPTY
```python
>>> numbers = [1, 2, 3]
>>> letters = ["a", "b", "c"]

>>> for number, letter in zip(numbers, letters):
...     print(number, "->", letter)
...
1 -> a
2 -> b
3 -> c
```

Chain iterates sequentially

```python
from itertools import chain
matrix = [
    [9, 3, 8],
    [4, 5, 2],
    [6, 4, 3],
]

for value in chain(*matrix):
    print(value**2)
```

When looping over a list and removing/adding to it, the iterable is changing so it is best to iterate over a copy of it by slicing:

```python
numbers = [2, 4, 6, 8]

for number in numbers[:]:
    if number % 2 == 0:
        numbers.remove(number)

numbers
```

Chain operators:

```python 
if a => 1 and a <= 10:

if 1 <= a <= 10:
```
With short-circuiting:
```python 
3 < 2 < (1//0)
```
would evaluate fine 

```a, b = b, a```

Good function defintion:
```python
def add_numbers(a: int | float, b: int | float) -> float:
    """Add numbers
    Args:
        a (int | float): First number
        b (int | float): Second number
    Raises:
        ValueError:
    Returns:
        float: Sum of a and b
    """
    a, b = float(a), float(b)
    return a + b

```

Long assert statements use backslash:
```python


number = 42

assert number > 0 and isinstance(number, int), \
    f"number greater than 0 expected, got: {number}"

def get_response(server, ports=(443, 80)):
    assert len(ports) > 0, f"ports expected a non-empty tuple, got {ports}"
    for port in ports:
        if server.connect(port):
            return server.get()
    return None
```

```python
print(f"{var=}")

print("""
line1
line2
line3
""")
```

Parsing CLI arguments:
```python
    def parse_args(argv=None):
    """Parse command line arguments.
    Args:
        argv (list): List of string arguments to parse. If None, use sys.argv. This is so the function can be called from Jupyter notebooks.
    Returns:
        dict: Dictionary of parameters.
    """
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Clustering')
    parser.add_argument('-i', '--input', dest='input_path', required=True, help='Input file name.')

    args = vars(parser.parse_args(argv))
    return args

    if __name__ == '__main__':
    kwargs = parse_args()
    main(**kwargs)
```