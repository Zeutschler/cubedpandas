import numpy as np

from cubedpandas.member import Member


class MemberMatch:

    def __init__(self, key, members: list[Member], mask: np.ndarray | None = None):
        self.members = members
        self.key = key
        self.mask: np.ndarray | None = mask

    def clear_mask(self):
        self.mask = None