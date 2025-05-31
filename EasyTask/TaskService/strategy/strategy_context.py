class StrategyContext:
    def __init__(self, strategies):
        self.strategies = strategies

    def apply_strategies(self, queryset, params):
        for strategy in self.strategies:
            queryset = strategy.apply(queryset, params)
        return queryset
