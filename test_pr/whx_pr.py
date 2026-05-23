from bisect import bisect_left, bisect_right
from math import log2


class AbyssSort:
    def __init__(self, key=None, reverse=False):
        self.key = key or (lambda x: x)
        self.reverse = reverse

    def __call__(self, data):
        a = [(self.key(v), i, v) for i, v in enumerate(data)]
        n = len(a)
        if n < 2:
            return list(data)

        minrun = self._minrun(n)
        runs = []
        i = 0

        while i < n:
            lo = i
            hi = self._scan_run(a, lo, n)
            run_len = hi - lo

            if run_len < minrun:
                force = min(minrun, n - lo)
                self._binary_insert(a, lo, lo + force, hi)
                hi = lo + force

            runs.append((lo, hi))
            self._collapse(a, runs)
            i = hi

        while len(runs) > 1:
            self._merge_at(a, runs, len(runs) - 2)

        out = [x[2] for x in a]
        if self.reverse:
            out.reverse()
        return out

    def _less(self, x, y):
        return (x[0], x[1]) < (y[0], y[1])

    def _minrun(self, n):
        r = 0
        while n >= 64:
            r |= n & 1
            n >>= 1
        return n + r

    def _scan_run(self, a, lo, hi):
        if lo + 1 == hi:
            return hi

        run_hi = lo + 2

        if self._less(a[run_hi - 1], a[lo]):
            while run_hi < hi and self._less(a[run_hi], a[run_hi - 1]):
                run_hi += 1
            a[lo:run_hi] = reversed(a[lo:run_hi])
        else:
            while run_hi < hi and not self._less(a[run_hi], a[run_hi - 1]):
                run_hi += 1

        return run_hi

    def _binary_insert(self, a, lo, hi, start):
        if start == lo:
            start += 1

        for i in range(start, hi):
            pivot = a[i]
            left, right = lo, i

            while left < right:
                mid = (left + right) >> 1
                if self._less(pivot, a[mid]):
                    right = mid
                else:
                    left = mid + 1

            j = i
            while j > left:
                a[j] = a[j - 1]
                j -= 1
            a[left] = pivot

    def _collapse(self, a, runs):
        while len(runs) > 1:
            n = len(runs)
            if n >= 3:
                x = runs[n - 3][1] - runs[n - 3][0]
                y = runs[n - 2][1] - runs[n - 2][0]
                z = runs[n - 1][1] - runs[n - 1][0]

                if x <= y + z or y <= z:
                    if x < z:
                        self._merge_at(a, runs, n - 3)
                    else:
                        self._merge_at(a, runs, n - 2)
                    continue

            if n >= 2:
                y = runs[n - 2][1] - runs[n - 2][0]
                z = runs[n - 1][1] - runs[n - 1][0]
                if y <= z:
                    self._merge_at(a, runs, n - 2)
                    continue

            break

    def _merge_at(self, a, runs, i):
        lo1, hi1 = runs[i]
        lo2, hi2 = runs[i + 1]

        left = a[lo1:hi1]
        right = a[lo2:hi2]

        p = q = 0
        k = lo1
        gallop = 7
        win_left = win_right = 0

        while p < len(left) and q < len(right):
            if self._less(right[q], left[p]):
                a[k] = right[q]
                q += 1
                k += 1
                win_right += 1
                win_left = 0

                if win_right >= gallop and p < len(left):
                    cut = self._gallop_right(left, right[q - 1], p, len(left))
                    while p < cut:
                        a[k] = left[p]
                        p += 1
                        k += 1
                    win_right = 0
                    gallop = max(1, gallop - 1)
            else:
                a[k] = left[p]
                p += 1
                k += 1
                win_left += 1
                win_right = 0

                if win_left >= gallop and q < len(right):
                    cut = self._gallop_left(right, left[p - 1], q, len(right))
                    while q < cut:
                        a[k] = right[q]
                        q += 1
                        k += 1
                    win_left = 0
                    gallop = max(1, gallop - 1)

            gallop += 1 if win_left + win_right == 0 else 0

        while p < len(left):
            a[k] = left[p]
            p += 1
            k += 1

        while q < len(right):
            a[k] = right[q]
            q += 1
            k += 1

        runs[i] = (lo1, hi2)
        del runs[i + 1]

    def _gallop_left(self, arr, key, lo, hi):
        last = lo
        step = 1

        while lo + step < hi and self._less(arr[lo + step], key):
            last = lo + step + 1
            step = (step << 1) + 1

        left = last
        right = min(lo + step + 1, hi)

        while left < right:
            mid = (left + right) >> 1
            if self._less(arr[mid], key):
                left = mid + 1
            else:
                right = mid

        return left

    def _gallop_right(self, arr, key, lo, hi):
        last = lo
        step = 1

        while lo + step < hi and not self._less(key, arr[lo + step]):
            last = lo + step + 1
            step = (step << 1) + 1

        left = last
        right = min(lo + step + 1, hi)

        while left < right:
            mid = (left + right) >> 1
            if self._less(key, arr[mid]):
                right = mid
            else:
                left = mid + 1

        return left


def abyss_sort(data, key=None, reverse=False):
    return AbyssSort(key=key, reverse=reverse)(data)


a = [5, 1, 9, 3, 3, 7, 2, 8, 4, 6]
print(abyss_sort(a))