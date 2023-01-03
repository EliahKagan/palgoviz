-- Generate the first 5000 Fibonacci numbers, F(0) to F(4999).
-- SPDX-License-Identifier: 0BSD

fibonacci :: Integer -> Integer

fibonacci n = fib 0 1 n where
    fib a b 0 = a
    fib a b n' = fib b (a + b) (n' - 1)

main =
    writeFile "fib5k.txt" $ unlines $ map (show . fibonacci) [0..4999]
