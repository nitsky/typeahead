# typeahead

Solution to [Quora "Typeahead Search" Challenge](https://www.quora.com/challenges#typeahead_search).

To run:

```bash
cat sample.txt | python typeahead.py
```

Below is an example input.

```
15
ADD user u1 1.0 Adam D’Angelo
ADD user u2 1.0 Adam Black
ADD topic t1 0.8 Adam D’Angelo
ADD question q1 0.5 What does Adam D’Angelo do at Quora?
ADD question q2 0.5 How did Adam D’Angelo learn programming?
QUERY 10 Adam
QUERY 10 Adam D’A
QUERY 10 Adam Cheever
QUERY 10 LEARN how
QUERY 1 lear H
QUERY 0 lea
WQUERY 10 0 Adam D’A
WQUERY 2 1 topic:9.99 Adam D’A
DEL u2
QUERY 2 Adam
```

Here is the expected output:

```
u2 u1 t1 q2 q1
u1 t1 q2 q1

q2
q2

u1 t1 q2 q1
t1 u1
u1 t1
```

