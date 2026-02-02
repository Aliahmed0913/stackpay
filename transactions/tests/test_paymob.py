import pytest
import requests
from rest_framework import status
from ..services.paymob import ProviderServiceError


@pytest.mark.django_db()
class TestPayMobService:
    def test_correct_currency(self, customer_factory, paymob_factory):
        customer = customer_factory(
            username="Currency_return", email="Currency-return009@gmail.com"
        )
        paymob = paymob_factory(customer)
        currency, _ = paymob.country_native_currencies()
        assert currency == "EGP"

    @pytest.mark.parametrize(
        "have_address,country",
        [(False, None), (True, "SD")],  # no main address raise error here
    )  # unsupported country raise error here
    def test_fail_currency(
        self, customer_factory, paymob_factory, have_address, country
    ):
        customer = customer_factory(with_address=have_address, country=country)
        paymob = paymob_factory(customer)

        with pytest.raises(ProviderServiceError):
            paymob.country_native_currencies()

    def test_request_field(self, customer_factory, paymob_factory, mock_post):
        customer = customer_factory(with_address=False)
        paymob = paymob_factory(customer)

        mock_post.status_code = status.HTTP_200_OK
        mock_post.json.return_value = {"request_field": "success"}
        result = paymob._request_field(
            payload={"fake": "data"},
            endpoint="http://fake.paymob/api",
            requested_field="request_field",
            field_name="testcase",
        )
        assert result == "success"

    @pytest.mark.parametrize(
        "status_code,return_value",
        [
            (status.HTTP_200_OK, {}),  # missing field
            (status.HTTP_400_BAD_REQUEST, None),
        ],
    )  # http error
    def test_request_field_fail(
        self, customer_factory, paymob_factory, status_code, return_value, mock_post
    ):
        customer = customer_factory(with_address=False)
        paymob = paymob_factory(customer)

        mock_post.status_code = status_code
        mock_post.json.return_value = return_value

        if status_code == status.HTTP_400_BAD_REQUEST:
            mock_post.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "Bad Request"
            )
        with pytest.raises(ProviderServiceError):
            paymob._request_field(
                payload={"fake": "data"},
                endpoint="http://fake.paymob/api",
                requested_field="not_found",
                field_name="testfield",
            )
