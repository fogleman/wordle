from collections import Counter, defaultdict
import random

def load_words(path):
    with open(path) as fp:
        return fp.read().split('\n')

all_words = load_words('all.txt')
top_words = load_words('top.txt')

print(len(all_words))
print(len(top_words))

def make_hint(answer, guess):
    result = ['x'] * len(answer)
    available = Counter(answer)
    for i, (a, c) in enumerate(zip(answer, guess)):
        if a == c:
            result[i] = '✓'
            available[c] -= 1
    for i, (a, c) in enumerate(zip(answer, guess)):
        if a != c and available[c] > 0:
            result[i] = '~'
            available[c] -= 1
    return ''.join(result)

class State:
    def __init__(self):
        self.knowns = [''] * 5
        self.counts = []

    def key(self):
        knowns = tuple(self.knowns)
        counts = tuple(sorted(set(self.counts)))
        return (knowns, counts)

    def copy(self):
        s = State()
        s.knowns = list(self.knowns)
        s.counts = list(self.counts)
        return s

    def update(self, guess, hint):
        unknown_hints = defaultdict(list) # c => ['x', '~']
        unknown_positions = defaultdict(set) # c => {1, 3}
        for i, (c, h) in enumerate(zip(guess, hint)):
            if h == '✓':
                self.knowns[i] = c
            else:
                unknown_hints[c].append(h)
                unknown_positions[c].add(i)
        unknown_indexes = {i for i in range(5) if not self.knowns[i]}
        for c, hints in unknown_hints.items():
            other_indexes = tuple(sorted(unknown_indexes - unknown_positions[c]))
            these_indexes = tuple(sorted(unknown_positions[c]))
            if 'x' in hints and '~' in hints:
                # exact number known ==
                n = hints.count('~')
                self.counts.append((other_indexes, c, '==' , n))
                self.counts.append((these_indexes, c, '==' , 0))
            elif '~' in hints:
                # minimum bound known >=
                n = hints.count('~')
                self.counts.append((other_indexes, c, '>=' , n))
                self.counts.append((these_indexes, c, '==' , 0))
            else:
                # zero
                n = hints.count('~')
                self.counts.append((tuple(sorted(unknown_indexes)), c, '==' , n))

    def match(self, word):
        for i, c in enumerate(word):
            if self.knowns[i] and c != self.knowns[i]:
                return False
        for indexes, c, op, n in self.counts:
            m = [word[i] for i in indexes].count(c)
            if op == '==':
                if m != n:
                    return False
            else:
                if m < n:
                    return False
        return True

    def filter_words(self, words):
        return [w for w in words if self.match(w)]

    def rank_words(self, words):
        all_words = list(words)
        words = self.filter_words(words)
        memo = {}
        results = []
        for guess in words:
            count = total = 0
            for answer in words:
                s = self.copy()
                hint = make_hint(answer, guess)
                s.update(guess, hint)
                key = s.key()
                if key not in memo:
                    candidates = s.filter_words(top_words)
                    memo[key] = len(candidates)
                count += memo[key]
                total += 1
            # print(guess, count / total)
            results.append((count / total, guess))
        results.sort()
        for score, word in results:
            print(word, score)

# x -> zero
# xx -> zero
# ~x -> one, none of these positions
# ~~ -> two or more, none of these positions
# xxx -> zero
# ~xx -> one, none of these positions
# ~~x -> two, none of these positions
# ~~~ -> three or more, none of these positions

# while True:
#     answer = random.choice(top_words)
#     # if make_hint(answer, 'suave') != '✓xxx~':
#     #     continue
#     # guess = random.choice(all_words)
#     s = State()
#     rules = []
#     for i in range(6):
#         guess = input().strip()
#         hint = make_hint(answer, guess)
#         s.update(guess, hint)
#         # rules.extend(make_rules(guess, hint))
#         candidates = s.filter_words(top_words)
#         print(len(candidates), answer in candidates, candidates)
#         print(s.knowns)
#         for x in s.counts:
#             print(x)
#         print(guess)
#         print(hint)

# memo = {}
# for guess in all_words:
#     count = total = 0
#     for answer in top_words:
#         s = State()
#         hint = make_hint(answer, guess)
#         s.update(guess, hint)
#         key = s.key()
#         if key not in memo:
#             candidates = s.filter_words(top_words)
#             memo[key] = len(candidates)
#         count += memo[key]
#         total += 1
#     print(guess, count / total)
