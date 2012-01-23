#-*- coding: utf-8 -*-
from django.db.utils import IntegrityError
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from django.conf import settings

from django_any.utils import split_model_kwargs, NO_RETURNED_VALUE

SAVE_RETRIES = getattr(settings, 'DJANGO_ANY_SAVE_RETRIES', 10)

class BaseValueGenerator(object):
    hooks = None

    def register(self, cls, impl=None):
        """
        Registers desired type with django_any.
        """
        def _wrapper(func):
            self.registry[cls] = func
            return func

        if impl:
            return _wrapper(impl)
        return _wrapper

    def add_rule(self, func):
        """
        Add a rule for generating value.

        This function can be used as a decorator.
        """
        self.hooks.append(func)
        return func

    def __call__(self, *args, **kwargs):
        for hook in self.hooks:

            out = hook(*args, **kwargs)
            if out:
                return out.value

        # If no hooks returned, return normally.
        return self._generate_value(*args, **kwargs)

    def _generate_value(self, *args, **kwargs):
        """
        Generate value, implemented by subclassses.
        """
        raise NotImplementedError()


class BaseFieldValueGenerator(BaseValueGenerator):
    def __init__(self, registry):
        self.registry = registry
        self.hooks = []

    def _generate_value(self, *args, **kwargs):
        try:
            field = args[0]
        except IndexError:
            raise DjangoAnyError("Field is not provided")

        field_type = field.__class__

        try:
            function = self.registry[field_type]
        except KeyError:

            # Quite often the sample value for the parent
            # field will do just as well.
            for parent in field_type.__mro__[1:]:
                if parent in self.registry:
                    return self.registry[parent](*args, **kwargs)
            raise DjangoAnyError("no match %s" % field_type)

        return function(*args, **kwargs)

class FieldValueGenerator(BaseFieldValueGenerator):
    pass

class FormFieldValueGenerator(BaseFieldValueGenerator):
    pass

class BaseClassValueGenerator(BaseValueGenerator):
    def __init__(self, registry, field_generator):
        self.hooks = []
        self.registry = registry
        self.field_generator = field_generator

    def _generate_value(self, *args, **kwargs):
        try:
            model = args[0]
        except IndexError:
            raise DjangoAnyError("Model is not provided")

        return self.registry.get(model, self.default)(*args, **kwargs)

    def default(self, *args, **kw):
        #: Subclasses should override.
        raise NotImplementedError()

class ModelValueGenerator(BaseClassValueGenerator):
    def default(self, model_cls, **kwargs):
        result = model_cls()

        attempts = SAVE_RETRIES
        while True:
            try:
                self._fill_model_fields(result, **kwargs)
                result.full_clean()
                result.save()
                return result
            except (IntegrityError, ValidationError):
                attempts -= 1
                if not attempts:
                    raise

    def _fill_model_fields(self, model, **kwargs):
        model_fields, fields_args = split_model_kwargs(kwargs)

        # Fill in virtual fields.
        for field in model._meta.virtual_fields:
            if field.name in model_fields:
                object = kwargs[field.name]
                model_fields[field.ct_field] =\
                    kwargs[field.ct_field] = ContentType.objects.get_for_model(object)
                model_fields[field.fk_field] =\
                    kwargs[field.fk_field] = object.pk

        # Fill in local fields.
        for field in model._meta.fields:
            if field.name in model_fields:
                if isinstance(kwargs[field.name], Q):

                    # Lookup ForeingKey field in DB.
                    key_field = model._meta.get_field(field.name)
                    value = key_field.rel.to.objects.get(kwargs[field.name])
                    setattr(model, field.name, value)
                else:
                    # TODO support any_model call
                    setattr(model, field.name, kwargs[field.name])
            elif isinstance(field, models.OneToOneField)\
                        and field.rel.parent_link:
                # Skip link to parent instance.
                pass
            elif isinstance(field, models.fields.AutoField):
                # Skip primary key field.
                pass
            elif isinstance(field, models.fields.related.ForeignKey) \
                        and field.model == field.rel.to:
                # Skip self relations.
                pass
            else:
                setattr(model, field.name,
                        self.field_generator(field, **fields_args[field.name]))

        # Process OneToOne relations.
        one_to_ones = [(relation.var_name, relation.field)\
                        for relation in model._meta.get_all_related_objects()\
                            if relation.field.unique] # TODO and not relation.field.rel.parent_link ??

        for field_name, field in one_to_ones:
            if field_name in model_fields:
                # TODO support any_model call
                setattr(model, field_name, kwargs[field_name])


class FormValueGenerator(BaseClassValueGenerator):
    def default(self, form_cls, **kwargs):
        form_data = {}
        form_files = {}

        form_fields, fields_args = split_model_kwargs(kwargs)

        for name, field in form_cls.base_fields.iteritems():
            if name in form_fields:
                form_data[name] = kwargs[name]
            else:
                form_data[name] = self.field_generator(field,
                                                       **fields_args[name])

        return form_data, form_files

class DjangoAnyError(Exception):
    pass