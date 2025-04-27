from .numbergen import IncrementalNumberGenerator


DEFAULT_REF_START = 5001


class RefStore:
    def __init__(self):
        self.refs = {}
        self._refgen = IncrementalNumberGenerator(DEFAULT_REF_START)

    def getRef(self, identifier: str) -> int:
        if identifier in self.refs:
            return self.refs[identifier]
        else:
            ref = self._refgen.next()
            self.refs[identifier] = ref
            return ref
