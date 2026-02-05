from typing import Literal, Optional, Union
from pydantic import BaseModel, Field


class BaseSettings(BaseModel):

    def __repr__(self):
        return self.model_dump_json(indent=5)

    def __str__(self):
        return self.__repr__()


class ClientCookieJar(BaseSettings):
    unsafe: bool = True


class ClientConnector(BaseSettings):
    ssl: bool = True


class ClientTimeout(BaseSettings):
    sock_connect: int
    sock_read: int


class ClientSettings(BaseSettings):
    cookie_jar: ClientCookieJar = Field(default_factory=ClientCookieJar)
    connector: ClientConnector = Field(default_factory=ClientConnector)
    timeout: ClientTimeout = Field(default_factory=ClientTimeout)


class SynchronousClient(BaseSettings):
    settings: ClientSettings = Field(default_factory=lambda: ClientSettings(
        timeout=ClientTimeout(sock_connect=30, sock_read=60)
    ))


class AsynchronousClient(BaseSettings):
    settings: ClientSettings = Field(default_factory=lambda: ClientSettings(
        timeout=ClientTimeout(sock_connect=5, sock_read=10)
    ))


SSLCloudServices = Union[Literal["prompt"], bool]


class CloudServices(BaseSettings):
    ssl: SSLCloudServices = 'prompt'


class EdgeClient(SynchronousClient):
    services: CloudServices = Field(default_factory=CloudServices)


class Drive(BaseSettings):
    syn: SynchronousClient = Field(default_factory=SynchronousClient)


class Edge(BaseSettings):
    syn: EdgeClient = Field(default_factory=EdgeClient)
    asyn: AsynchronousClient = Field(default_factory=AsynchronousClient)


class Portal(BaseSettings):
    syn: SynchronousClient = Field(default_factory=SynchronousClient)
    asyn: AsynchronousClient = Field(default_factory=AsynchronousClient)


class Streamer(BaseSettings):
    max_workers: int = 20


class DirectIO(BaseSettings):
    api: AsynchronousClient = Field(default_factory=AsynchronousClient)
    storage: AsynchronousClient = Field(default_factory=AsynchronousClient)
    streamer: Streamer = Field(default_factory=Streamer)


class IO(BaseSettings):
    direct: DirectIO = Field(default_factory=DirectIO)
    downloads: str = '~/Downloads'


class Postman(BaseSettings):
    enabled: bool = False
    filename: Optional[str] = None


class Settings(BaseSettings):
    core: Portal = Field(default_factory=Portal)
    edge: Edge = Field(default_factory=Edge)
    drive: Drive = Field(default_factory=Drive)
    io: IO = Field(default_factory=IO)
    audit: Postman = Field(default_factory=Postman)
