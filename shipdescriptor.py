class ShipDescriptor:
    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if self.name == '_tp' and value not in (1, 2):
            return
        elif self.name in ('_x', '_y', '_length') and type(value) != int:
            return
        elif self.name == '_is_move' and type(value) != bool:
            return
        setattr(instance, self.name, value)
