from django.forms import ValidationError
from user_auth_app.models import Customer, BusinessPartner
from coderr_app.models import OfferDetail, Order
from django_filters import rest_framework as filters
from datetime import timedelta
from coderr_app.models import Offer

class OfferFilter(filters.FilterSet):
    max_delivery_time = filters.NumberFilter(method='filter_max_delivery_time')

    def filter_max_delivery_time(self, queryset, name, value):
        try:
            max_days = int(value)
            if max_days < 0:
                return queryset.none()
            return queryset.filter(min_delivery_time__lte=max_days)
        except (ValueError, TypeError):
            return queryset.none()

    class Meta:
        model = Offer
        fields = ['min_price', 'max_delivery_time']


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
    
def filter_review_query(self, queryset):
    business_user_id = self.request.query_params.get('business_user_id')
    reviewer_id = self.request.query_params.get('reviewer_id')
    if business_user_id:
        return queryset.filter(business_user_id=business_user_id)
    if reviewer_id:
        return queryset.filter(reviewer_id=reviewer_id)
    else:
        return queryset