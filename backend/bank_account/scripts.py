from django.utils.timezone import make_aware
from datetime import datetime,time

def filter_query(query_set,filters):
    operation_type = filters.get("operation_type",None)
    dates = filters.get("dates",None)
    order = filters.get("order","desc")

    new_query = query_set
    if operation_type:
        new_query = query_set.filter(operation=operation_type)
    if dates:
        max_date = make_aware(datetime.combine(dates[1],time.max))
        min_date = make_aware(datetime.combine(dates[0],time.min))
        new_query =new_query.filter(date__range=[min_date, max_date])

    if(order):
        if order == "asc":
            order = "date"
        elif order == "desc":
            order = "-date"
    new_query = new_query.order_by(order)

    return new_query
                         