def get_model_class_name(model):
    return str(model).rsplit(".").pop().split("'")[0]
