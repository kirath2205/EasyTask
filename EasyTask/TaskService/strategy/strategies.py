# strategies.py
from abc import ABC, abstractmethod


class TaskStrategy(ABC):
    @abstractmethod
    def apply(self, queryset, params):
        pass


class TaskFilterStrategy(TaskStrategy):
    def apply(self, queryset, params):
        status = params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        frequency = params.get('frequency')
        if frequency:
            queryset = queryset.filter(frequency=frequency)

        priority = params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset


class TaskSortingStrategy(TaskStrategy):
    def apply(self, queryset, params):
        ordering = params.get('sort')
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset
