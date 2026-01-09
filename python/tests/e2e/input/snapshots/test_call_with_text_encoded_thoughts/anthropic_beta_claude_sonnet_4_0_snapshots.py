from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response": """\
**Thinking:**
  I need to find the first Fibonacci number that ends in 57. Let me calculate some Fibonacci numbers:
  \n\
  F(1) = 1
  F(2) = 1  \n\
  F(3) = 2
  F(4) = 3
  F(5) = 5
  F(6) = 8
  F(7) = 13
  F(8) = 21
  F(9) = 34
  F(10) = 55
  F(11) = 89
  F(12) = 144
  F(13) = 233
  F(14) = 377
  F(15) = 610
  F(16) = 987
  F(17) = 1597
  F(18) = 2584
  F(19) = 4181
  F(20) = 6765
  F(21) = 10946
  F(22) = 17711
  F(23) = 28657
  \n\
  F(23) = 28657 ends in 57! This is the first one.
  \n\
  Now I need to check if 28657 is prime. This is a fairly large number to check by hand, but I should be able to determine this.

28657\
"""
    }
)
