# create DB
from project import db,create_app, models
app = create_app()
app.app_context().push()
db.create_all()