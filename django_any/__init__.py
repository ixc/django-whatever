# -*- coding: utf-8 -*-
from django_any.value_generator import ModelValueGenerator, FieldValueGenerator,\
    FormValueGenerator, FormFieldValueGenerator

field_registry = {}
model_registry = {}
form_field_registry = {}
form_registry = {}

any_field = FieldValueGenerator(field_registry)
any_model = ModelValueGenerator(model_registry, any_field)

any_form_field = FormFieldValueGenerator(form_registry)
any_form = FormValueGenerator(form_field_registry, any_form_field)

__version__ = (0, 2, 3, 'final', 0)