import supabase, os
from pathlib import Path
from typing import Tuple

class FileUpload:
    __supabase_client: supabase.Client

    def __init__(self):
        self.__supabase_client = supabase.create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

    def upload_file(self, file: Path, file_name: str) -> Tuple[bool, str | None]:
        resp = self.__supabase_client.storage.from_('invoices').upload(file_name, file, file_options={"content-type": "application/pdf"})
        if resp.is_error:
            return False, None
        url = self.__supabase_client.storage.from_('invoices').get_public_url(file_name)
        return True, url