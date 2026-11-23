# Algorithm Paradigm & Data Structure Selection Matrix

## 1. Problem Signature -> Canonical Pattern

| Problem Signature / Query Pattern | Best Data Structure / Algorithm | Time / Space | Classic Trap |
| :--- | :--- | :--- | :--- |
| Contiguous subarray with sum/unique constraint (monotone predicate) | **Two Pointers / Sliding Window** | $O(N)$ / $O(1..K)$ | Fails on negative weights if monotonicity breaks -> use Prefix Sum + Hash Map / Monotonic Deque. |
| Next greater/smaller element; sliding-window min/max | **Monotonic Stack / Monotonic Deque** | $O(N)$ / $O(N)$ | Confusing strict `<` vs `<=` when duplicate elements appear (causes double counting!). |
| Minimize max / maximize min over a monotonic feasibility check | **Binary Search on the Answer** + greedy `feasible(x)` | $O(T_{\text{check}} \log R)$ | Off-by-one infinite loop on `mid = (lo + hi) // 2` when updating `lo = mid` (use `mid = (lo + hi + 1) // 2`). |
| Dynamic connectivity, Kruskal MST, equivalence classes | **Disjoint Set Union (Union-Find)** with path compression + union by size | $O(\alpha(N))$ | Union-Find does not support arbitrary edge deletions offline without a segment-tree-over-time rollback DSU. |
| Point updates + prefix/range sum queries | **Fenwick Tree (BIT)** | $O(\log N)$ / $O(N)$ | 1-indexed bit arithmetic (`i += i & -i`); use Segment Tree for arbitrary associative range ops (`min`/`max`/lazy). |
| Static range `min`/`max`/`gcd` queries (no updates) | **Sparse Table** | $O(N \log N)$ build, **$O(1)$** query | $O(1)$ overlap trick only works on **idempotent** ops (`min`, `max`, `gcd`, bitwise OR/AND), not `sum`! |
| Shortest path: unweighted / $\{0,1\}$ weights / $\ge 0$ weights / negative weights | **BFS** / **0-1 Deque BFS** / **Dijkstra** / **Bellman–Ford** | $O(V+E)$ to $O(VE)$ | Running Dijkstra with negative edges; pushing stale heap entries without `if d > dist[u]: continue`. |
| Dependency ordering, cycle detection, longest path on DAG | **Kahn's Topological Sort + DAG DP** | $O(V+E)$ | If `len(order) < V`, a cycle exists—handle explicitly! |
| Bipartite matching, project selection, min-cut partitioning | **Dinic's Max-Flow / Hopcroft–Karp** | $O(E\sqrt{V})$ (unit/bipartite) | Forgetting reverse residual edges with initial capacity `0` (`edge ^ 1`). |
| Multi-pattern substring search / prefix autocomplete | **Trie** or **Aho–Corasick Automaton**; single-pattern: **KMP / Z-algorithm** | $O(\sum |P| + |T|)$ | Single-modulus rolling hash collisions -> use 61-bit Mersenne prime $2^{61}-1$ or double hashing. |
| High-throughput membership / frequency / cardinality at massive scale | **Bloom Filter** / **Count-Min Sketch** / **HyperLogLog** | $O(1)$ update, sublinear RAM | Bloom filters have configurable false-positive rate $\epsilon$ and do not support deletion (use Counting/Cuckoo filter). |
| High-dimensional vector nearest-neighbor search | **HNSW** / **IVF-PQ** | Sublinear query | Exact k-NN degrades to $O(ND)$ due to curse of dimensionality ($D > 32$). |

## 2. Dynamic Programming Optimization Checklist

1. **Space Rolling**: If `dp[i][*]` only reads `dp[i-1][*]`, keep 2 rows (`prev, curr`), or 1 row iterating `j` backward (0/1 knapsack) vs. forward (unbounded knapsack).
2. **Prefix / Fenwick / Monotonic Queue Optimization**: When transition is `dp[i] = min_{j in [i-W, i-1]} (dp[j] + c[j]) + w[i]`, drop $O(NW) \to O(N)$ with a monotonic deque.
3. **Convex Hull Trick / Li Chao Tree**: When `dp[i] = min_{j < i} (m_j * x_i + b_j)` forms linear functions, drop $O(N^2) \to O(N \log N)$ (or $O(N)$ if slopes and queries are monotonic).
4. **Divide & Conquer / Knuth Optimization**: Applies when optimal split point `opt[i][j]` satisfies quadrangle inequality (`opt[i][j-1] <= opt[i][j] <= opt[i+1][j]`).
