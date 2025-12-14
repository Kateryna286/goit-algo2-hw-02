def find_min_max(arr):
    if not arr:
        raise ValueError("Array must not be empty")

    def helper(left, right):
        if left == right:
            return arr[left], arr[left]

        if right == left + 1:
            if arr[left] < arr[right]:
                return arr[left], arr[right]
            return arr[right], arr[left]

        mid = (left + right) // 2
        min_l, max_l = helper(left, mid)
        min_r, max_r = helper(mid + 1, right)

        return min(min_l, min_r), max(max_l, max_r)

    return helper(0, len(arr) - 1)


if __name__ == "__main__":
    # demo
    arr = [2, -4, 1, 9, -6, 7, -3]
    mn, mx = find_min_max(arr)
    print("Array:", arr)
    print("Min:", mn)
    print("Max:", mx)

    # tests
    assert find_min_max([2, -4, 1, 9, -6, 7, -3]) == (-6, 9)
    assert find_min_max([5]) == (5, 5)
    assert find_min_max([1, 2]) == (1, 2)
    assert find_min_max([2, 1]) == (1, 2)
    assert find_min_max([3, 3, 3]) == (3, 3)
    
    # empty array test
    try:
        find_min_max([])
        assert False, "Expected ValueError for empty array"
    except ValueError:
        pass

    print("All tests passed.")
