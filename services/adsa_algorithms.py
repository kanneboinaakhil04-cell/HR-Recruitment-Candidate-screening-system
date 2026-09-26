"""
ADSA (Advanced Data Structures & Algorithms) Implementation
Demonstrating algorithm design & optimization concepts in HR Screening:
1. Custom QuickSort Algorithm for candidate match ranking
2. Trie Data Structure for efficient skill prefix searching & indexing
3. Hash-Table based candidate filtering
"""

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.skill_name = None

class SkillTrie:
    """
    Trie (Prefix Tree) Data Structure for ultra-fast skill lookup and prefix autocompletion.
    Time Complexity:
    - Insert: O(L) where L is skill length
    - Search: O(L)
    - Prefix Search: O(P + N) where P is prefix length and N is matching nodes
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, skill_name):
        node = self.root
        clean_name = skill_name.strip().lower()
        for char in clean_name:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.skill_name = skill_name

    def search_exact(self, skill_name):
        node = self.root
        clean_name = skill_name.strip().lower()
        for char in clean_name:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def find_skills_with_prefix(self, prefix):
        node = self.root
        clean_prefix = prefix.strip().lower()
        for char in clean_prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        results = []
        self._dfs_collect(node, results)
        return results

    def _dfs_collect(self, node, results):
        if node.is_end_of_word:
            results.append(node.skill_name)
        for char, child_node in node.children.items():
            self._dfs_collect(child_node, results)


def quicksort_candidates(candidates_list, key_func=lambda x: x['match_score'], reverse=True):
    """
    ADSA QuickSort Algorithm implementation to sort candidates by score.
    Divide and Conquer strategy.
    Average Time Complexity: O(N log N)
    Space Complexity: O(log N) recursion stack
    """
    if len(candidates_list) <= 1:
        return candidates_list

    pivot = candidates_list[len(candidates_list) // 2]
    pivot_val = key_func(pivot)

    left = []
    middle = []
    right = []

    for item in candidates_list:
        val = key_func(item)
        if val > pivot_val:
            left.append(item)
        elif val < pivot_val:
            right.append(item)
        else:
            middle.append(item)

    if reverse:
        # Descending order (Highest match score first)
        return quicksort_candidates(left, key_func, reverse) + middle + quicksort_candidates(right, key_func, reverse)
    else:
        # Ascending order
        return quicksort_candidates(right, key_func, reverse) + middle + quicksort_candidates(left, key_func, reverse)


def filter_candidates_hashtable(candidates, filter_key, filter_val):
    """
    Hash Table Indexing for O(1) Candidate Attribute Filtering.
    """
    hash_index = {}
    for candidate in candidates:
        val = candidate.get(filter_key, "All")
        if val not in hash_index:
            hash_index[val] = []
        hash_index[val].append(candidate)
        
    return hash_index.get(filter_val, [])
