import numpy as np

K = 4   # A small constant to favor variables appearing in both polarities

def calculate_score(pos_counts, neg_counts):
    total_counts = pos_counts + neg_counts
    score = (total_counts * (2**K)) + (pos_counts * neg_counts)
    best_var_idx = np.argmax(score)

    if pos_counts[best_var_idx] >= neg_counts[best_var_idx]:
        return int(best_var_idx + 1)
    else:
        return int(-(best_var_idx + 1))

