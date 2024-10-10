from abc import ABCMeta, abstractmethod


class VectorStoreIndex(metaclass=ABCMeta):
    @abstractmethod
    def create_vector_db(self):
        pass

    @abstractmethod
    def get_vector_store_index(self, recreate_index=False):
        pass