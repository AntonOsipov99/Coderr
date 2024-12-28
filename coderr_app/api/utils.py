from django.forms import ValidationError
from user_auth_app.models import Customer, BusinessPartner
from coderr_app.models import OfferDetail, Order


def order_references_and_validate(offer_detail_id, authenticated_user):

    def get_object_or_raise(model, condition, error_message):
        try:
            return model.objects.get(**condition)
        except model.DoesNotExist:
            raise ValidationError({"detail": error_message})

    offer_detail = get_object_or_raise(OfferDetail, {'id': offer_detail_id}, f"OfferDetail with id {offer_detail_id} does not exist.")
    customer = get_object_or_raise(Customer, {'user': authenticated_user}, f"Customer account of {authenticated_user} does not exist.")
    business = get_object_or_raise(BusinessPartner, {'id': offer_detail.offer.user.id}, f"Business account of {offer_detail.offer.user} does not exist.")

    return offer_detail, customer, business

def create_order_object(business, customer, offer_detail):
    return Order.objects.create(
        customer_user=customer,
        business_user=business,
        title=offer_detail.title,
        revisions=offer_detail.revisions,
        delivery_time_in_days=offer_detail.delivery_time_in_days,
        price=offer_detail.price,
        features=offer_detail.features,
        offer_type=offer_detail.offer_type,
        status='in_progress'
    )