def segments_intersect(seg1, seg2):
    return max(seg1[0], seg2[0]) > min(seg1[1], seg2[1])
