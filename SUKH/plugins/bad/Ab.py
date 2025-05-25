from SUKH import app
from pyrogram.modules.edit_text_delete import get_edited_text_delete_handler

def register_edit_handler():
    handler = get_edited_text_delete_handler()
    app.add_handler(handler)
