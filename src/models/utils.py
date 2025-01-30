def get_model_class_name(model):
    return str(type(model)).rsplit(".").pop().split("'")[0]
