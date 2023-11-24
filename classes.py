class digitalBuilds:
    def __init__(self):
        self.builds = []

    @property
    def get(self):
        return self.builds
    
    def add(self, block):
        self.builds.append(block)

    def remove(self, block):
        if block in self.builds:
            self.builds.remove(block)
            


class Block:
    def __init__(self, filters, metric, value):
        self.__filters = filters
        self.__metric = metric
        self.__value = value
        
    @property
    def filters(self):
        return self.__filters
    
    @property
    def metric(self):
        return self.__metric
        
    @property
    def value(self):
        return self.__value
    
    
    @property
    def list(self):
        filters_formatted = "\n".join([f"{key}: {', '.join(values)}" for key, values in self.__filters.items()])
        change_formatted = f"Change: {self.__value}% to {self.__metric}"

        return f"**Filters:**\n{filters_formatted}\n\n**{change_formatted}**"