import pytest
from django.contrib.auth import get_user_model
from db_app.models import Docs, UsersToDocs, Price, Cart
from django.db import models

User = get_user_model()

@pytest.mark.django_db
class TestDocsModel:
    def test_fields(self):
        field_map = {field.name: field for field in Docs._meta.fields}

        assert isinstance(field_map['file_path'], models.CharField)
        assert field_map['file_path'].max_length == 255

        assert isinstance(field_map['size'], models.PositiveIntegerField)
        assert field_map['size'].help_text == "Размер файла в Кб"

        assert isinstance(field_map['extracted_text'], models.TextField)
        assert field_map['extracted_text'].null is True
        assert field_map['extracted_text'].blank is True


@pytest.mark.django_db
class TestUsersToDocsModel:
    def test_fields(self):
        field_map = {field.name: field for field in UsersToDocs._meta.fields}

        assert isinstance(field_map['username'], models.CharField)
        assert field_map['username'].max_length == 150

        assert isinstance(field_map['docs_id'], models.ForeignKey)
        assert field_map['docs_id'].related_model == Docs


@pytest.mark.django_db
class TestPriceModel:
    def test_fields(self):
        field_map = {field.name: field for field in Price._meta.fields}

        assert isinstance(field_map['file_type'], models.CharField)
        assert field_map['file_type'].max_length == 10

        assert isinstance(field_map['price'], models.FloatField)
        assert field_map['price'].help_text == "Цена за 1 Кб"


@pytest.mark.django_db
class TestCartModel:
    def test_fields(self):
        field_map = {field.name: field for field in Cart._meta.fields}

        assert isinstance(field_map['user_id'], models.ForeignKey)
        assert field_map['user_id'].related_model == User

        assert isinstance(field_map['docs_id'], models.ForeignKey)
        assert field_map['docs_id'].related_model == Docs

        assert isinstance(field_map['order_price'], models.FloatField)

        assert isinstance(field_map['payment'], models.BooleanField)
        assert field_map['payment'].default is False


