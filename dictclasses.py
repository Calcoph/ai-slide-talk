class FullMessage:
    def __init__(self, prompt: str, message: str, username: str, lecture: str, language: str) -> None:
        self.prompt = prompt
        self.message = message
        self.username = username
        self.lecture = lecture
        self.language = language

    def to_dict(self) -> dict[str, str]:
        {
            "prompt": self.prompt,
            "message": self.message,
            "username": self.username,
            "lecture": self.lecture,
            "language": self.language
        }

class UserRegister:
    def __init__(self, email: str, username: str, password: bytes, open_api_key: bytes) -> None:
        self.email = email
        self.username = username
        self.password = password
        self.open_api_key = open_api_key

class StoredFileData:
    def __init__(self, username: str, lecture: str, pdf_id: str, index_faiss_id: str, index_pkl_id: str) -> None:
        self.username = username
        self.lecture = lecture
        self.pdf_id = pdf_id
        self.index_faiss_id = index_faiss_id
        self.index_pkl_id = index_pkl_id
