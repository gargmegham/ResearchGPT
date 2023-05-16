from pydantic import BaseModel


class ChatRoomCreate(BaseModel):
    """Chatroom create from search"""

    search: str


class ChatRoomUpdate(BaseModel):
    """Chatroom update title"""

    title: str


class Chatroom(BaseModel):
    """Chatroom"""

    id: int
    user_id: int
    title: str
    search: str

    class Config:
        orm_mode = True


class MessageFromWebsocket(BaseModel):
    """message from websocket"""

    msg: str
    chatroom_id: int


class InitMessage(BaseModel):
    """
    message to send to websocket on init
    """

    previous_chats: list[dict] | None = None
    chatroom_ids: list[int] | None = None
    init_callback: bool = True


class PubMedPaper(BaseModel):
    """
    PubMed paper:
      - pmid: "36960329",
      - volume: "7",
      - issue: "",
      - year: "2023",
      - month: "",
      - day: "",
      - pages: "100179",
      - issn: "2666-6235",
      - journal: "Journal of migration and health",
      - journalabbrev: "J Migr Health",
      - title: "Foreigners living in Tuscany at the time of coronavirus outbreak.",
      - abstract: "During the coronavirus outbreak, a worldwide state of emergency and lockdown significantly affected the volunteer services for foreigners. The SARS-CoV-2 surveillance program was strengthened among migrants arriving in Italy. However, few screening measures for SARS-CoV2 infection have been conducted on the foreign population already present in Italy. In Tuscany, a great effort was made to know the epidemiological features of coronavirus outbreaks in the foreigners. Based on these premises, this study describes the prevalence and characteristics of SARS-CoV-2 infection in foreigners present in the Tuscan territory during the months of the highest incidence of this pandemic.",
      - affiliation: "",
      - authors: "Silvestri C, Profili F, Bartolacci S, Voller F, Stasi C",
      - articleid: "36960329,PMC10022458,10.1016/j.jmh.2023.100179,S2666-6235(23)00029-6",
      - keywords: "",
      - lastname: "Silvestri, Profili, Bartolacci, Voller, Stasi",
      - put_in_tables: "<a href=\"https://pubmed.ncbi.nlm.nih.gov/36960329\">Foreigners living in Tuscany at the time of coronavirus outbreak.</a>",
      - date: "2023-01-01"
    """

    pmid: str | None
    year: str | None
    day: str | None
    month: str | None
    volume: str | None
    issue: str | None
    title: str
    affiliation: str | None
    abstract: str
    pages: str | None
    issn: str | None
    journalabbrev: str | None
    authors: str
    journal: str | None
    date: str | None
    put_in_tables: str | None
    keywords: str | None
    articleid: str | None
    lastname: str | None


class MessageToWebsocket(BaseModel):
    """
    message to send to websocket
        - msg: message to send
        - finish: whether the message is the last message
        - chatroom_id: chatroom id
        - is_user: whether the message is from user
        - init: whether the message is init message
        - model_name: model name
    """

    msg: str | None
    finish: bool
    chatroom_id: int
    is_user: bool
    init: bool = False
    model_name: str | None = None

    class Config:
        """
        orm_mode: whether to use orm mode
        """

        orm_mode = True


class SendToStream(BaseModel):
    """
    message to send to stream
        - role: role of the message
        - content: content of the message
    """

    role: str
    content: str

    class Config:
        orm_mode = True


class SendInitToWebsocket(BaseModel):
    """send init message to websocket"""

    content: str
    tokens: int
    is_user: bool
    timestamp: int
    model_name: str | None = None

    class Config:
        orm_mode = True
