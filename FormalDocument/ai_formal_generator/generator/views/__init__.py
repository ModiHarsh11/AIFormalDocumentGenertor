"""View package — re-exports all view functions for url routing."""

from .common import home  # noqa: F401

from .office_order import (  # noqa: F401
    generate_body,
    regenerate_office_body,
    update_office_body,
    result_office_order,
    office_order_form,
    download_pdf,
    download_docx,
)

from .circular import (  # noqa: F401
    generate_circular_body,
    regenerate_circular_body,
    update_circular_body,
    result_circular,
    circular_form,
    download_circular_pdf,
    download_circular_docx,
)

from .policy import (  # noqa: F401
    generate_policy_body,
    regenerate_policy_body,
    update_policy_body,
    result_policy,
    download_policy_pdf,
    download_policy_docx,
)

from .advertisement import (  # noqa: F401
    result_advertisement,
    download_advertisement_pdf,
    download_advertisement_docx,
)

# Auth views
from .auth_views import (  # noqa: F401
    register_view,
    login_view,
    logout_view,
    profile_view,
)

# Dashboard & document management
from .dashboard import (  # noqa: F401
    dashboard,
    document_view,
    document_edit,
    document_delete,
    download_doc_pdf,
    download_doc_docx,
)

