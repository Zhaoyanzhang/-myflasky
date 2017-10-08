from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)

from . import views, errors


#lastest edit on page 101, add some value that available to global, these value should stay in DIC.
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
