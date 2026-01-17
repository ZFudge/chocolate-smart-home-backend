class SingletonMeta(type):
    """
    Meta class for creating singleton classes.
    """
    _SINGLETONS = dict()

    def __call__(cls, *args, **kwargs):
        if cls.__name__ in SingletonMeta._SINGLETONS:
            return SingletonMeta._SINGLETONS[cls.__name__]
        instance = super().__call__(*args, **kwargs)
        SingletonMeta._SINGLETONS[cls.__name__] = instance
        return instance
