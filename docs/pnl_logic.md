# Lots and PnL Logic

### Long Positions

- Example 1
    * BUY 10 @ 20 [10]
    * SELL 10 @ 25 []
    * FINAL STATE = 0 LOTS, Pnl = 10 * 5 = 50

- EXAMPLE 2
    * BUY 10 @ 20 (1 LOT) [10]
    * BUY 5 @ 21 (2 LOTS) [10, 5]
    * SELL 3 @ 24 (2 LOTS) [7, 5]
    * FINAL STATE = 2 LOTS, Pnl = 3 * 4 = 12

- EXAMPLE 3
    * BUY 10 @ 20 (1 LOT) [10]
    * BUY 5 @ 21 (2 LOTS) [10, 5]
    * SELL 12 @ 24 (2 LOTS) [3]
    * FINAL STATE = 1 LOT, Pnl = (10 * 1) + (2 * 4) = 18

---

### Short Positions

- EXAMPLE 4
    * SELL 10 @ 20 [-10]
    * BUY 10 @ 18 []
    * FINAL STATE = 0 LOTS, Pnl = 10 * 2 = 20

- EXAMPLE 5
    * SELL 10 @ 20 [-10]
    * BUY 3 @ 19 [-7]
    * FINAL STATE = 1 LOT, Pnl = 3 * 1 = 3

- EXAMPLE 6
    * SELL 10 @ 20 [-10]
    * BUY 12 @ 19 [2]
    * FINAL STATE = 1 LOT, Pnl = 10 * 1 = 10

- EXAMPLE 6
    * SELL 10 @ 20 [-10]
    * SELL 12 @ 19 [-10, -12]
    * BUY 15 @ 10 [-7]
    * FINAL STATE = 1 LOT, Pnl = (10 * 10) + (5 * 9) = 145
