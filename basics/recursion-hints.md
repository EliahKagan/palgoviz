## Hints for `recursion.merge_sort_adaptive`

<details>
<summary><strong>Hint 1</strong> <em>(click to reveal/hide)</em></summary>

You run into Professor Run at the park where he runs backwards each morning. He
tells you that runs of equal (or similar) values can be treated as rising runs
or falling runs, so they won't break either kind of run if they appear within
it. Is the professor right? Of increasing, decreasing, nonincreasing, and
nondecreasing runs, which kinds should you detect?
</details>

<details>
<summary><strong>Hint 2</strong> <em>(click to reveal/hide)</em></summary>

Your algorithm may fail to sort some monotone inputs in O(n) time, but those
are fairly rare. To make up for it, your algorithm may succeed at sorting some
inputs with frequent direction changes in O(n) time. Whatever runs you take
advantage of, detecting all such runs will take O(n) time.
</details>

<details>
<summary><strong>Hint 3</strong> <em>(click to reveal/hide)</em></summary>

Concatenating two lists sometimes behaves as a two-way merge. When? Such a
merge is always stable. Why? Yet it's easy to accidentally design an unstable
sort based on this insight. Why is that? Also, concatenation and two-way merge
both take linear time. Yet this insight is still useful. How?
</details>
