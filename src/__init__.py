"""
This file makes the 'src' directory a Python package and handles
initialization tasks, such as ensuring all SQLAlchemy models are
discovered when the package is first imported.
"""
# Manually import all model modules to ensure SQLAlchemy's declarative base
# is aware of all tables before any application logic runs. The `_` prefix
# indicates these imports are for side effects (model registration) only.
from .amenities import models as _amenity_models
from .bookings import models as _booking_models
from .images import models as _image_models
from .listings import models as _listing_models
from .reviews import models as _review_models
from .users import models as _user_models
