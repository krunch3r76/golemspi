# view/predicatedlist.py

# import copy
import collections


class PredicatedList(collections.UserList):
    """

    MODIFIED:   flag set whenever a mutator is called
    filter_predicate:   test logic to include element from original
        list to mapped list
    _filterIndices: indices mapping to underlying master list
    LOCKED: flag indicating that refresh should not rebuild indices
    """

    def __init__(self, initlist=None):
        """initialize with optional initial list"""
        self._filter_predicates = dict()
        self.__filterPredicate = lambda a: True
        if initlist is not None and len(initlist) > 0:
            self._filterIndices = [i for i in range(len(initlist))]
        else:
            self._filterIndices = []
        self.MODIFIED = False
        self.LOCKED = False
        super().__init__(initlist)

    def lock(self):
        self.LOCKED = True

    def unlock(self):
        self.LOCKED = False

    # mutators (sets MODIFIED)
    def append(self, appended):
        # wraps UserList's append
        self.MODIFIED = True
        super().append(appended)

    def extend(self, other):
        # wraps UserList's extend
        self.MODIFIED = True
        super().extend(other)

    # accessors (invokes refresh)
    def index(self, item, *args):
        # override index to reference the filtered list
        self._refresh()
        filteredList = self._mapped_list()
        return filteredList.data.index(item, *args)

    def __len__(self):
        # wraps __len__
        self._refresh()
        return len(self._filterIndices)

    def __repr__(self):
        # override to return a string representation of the mapped list
        self._refresh()
        return str(self._mapped_list())

    # other
    def __getitem__(self, index_or_slice):
        """override UserList's subscript operator to return a mapped
        element or slice

        Args:
            index_or_slice: the index or slice to retrieve
        Pre:
            _refresh() has been called
        """
        if isinstance(index_or_slice, slice):
            return self.__class__(self._mapped_list(index_or_slice))

        return self.data[self._filterIndices[index_or_slice]]

    def _build_indices(self):
        # rebuild indices based on current filterPredicate
        if len(self._filter_predicates) > 0:
            filter_predicates = [
                filter_predicate
                for filter_predicate in self._filter_predicates.values()
            ]
            self._filterIndices = [
                i
                for i, elem in enumerate(self.data)
                if all(pred(elem) for pred in filter_predicates)
            ]
        else:
            self._filterIndices = [i for i in range(len(self.data))]
        # self._filterIndices = [
        #     i for i, e in enumerate(self.data) if self.__filterPredicate(e)
        # ]

    def _refresh(self, force=False):
        """check modification flag and rebuild indices as needed

        Args:
            force: True to rebuild indices even if not MODIFIED
        """
        if (self.MODIFIED or force) and not self.LOCKED:
            self._build_indices()
            self.MODIFIED = False

    def _mapped_list(self, optional_slice=None):
        """map to a standard list from the indices

        Args:
            optional_slice: optional slice object
        Returns:
            a standard list object
        Raises:
            TypeError when a non slice object is passed as the argument
        """

        if optional_slice is not None and not isinstance(optional_slice, slice):
            raise TypeError("only slice objects")
        if isinstance(optional_slice, slice):
            return [self.data[index] for index in self._filterIndices[optional_slice]]
        else:
            return [self.data[index] for index in self._filterIndices[:]]

    @property
    def filterPredicate(self):
        raise Exception("filterPredicate is an unreadable property")

    @filterPredicate.setter
    def filterPredicate(self, predicate):
        # set the filter predicate and force a rebuild of the indices
        self.__filterPredicate = predicate
        self._refresh(force=True)

    def add_filter_predicate(self, predicate_name, predicate_lambda):
        self._filter_predicates[predicate_name] = predicate_lambda

    def del_filter_predicate(self, predicate_name):
        try:
            del self._filter_predicates[predicate_name]
        except KeyError:
            pass
