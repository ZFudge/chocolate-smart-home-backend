import chocolate_smart_home.utils as utils


class ModelStrFormatter:
    """Provides methods for getting dev-friendly textual data of model objects."""
    def __str__(self):
        model_name = utils.get_model_class_name(type(self))

        attrs = (
            [column.key, getattr(self, column.key)]
            for column in self.__table__.columns
        )
        attrs_str = ", ".join(map(lambda x: "=".join(map(str, x)), attrs))

        return (f"{model_name}({attrs_str})")

    def __repr__(self):
        return str(self)
