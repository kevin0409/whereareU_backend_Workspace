from pydantic import BaseModel, Field
from typing import List

# Define request and response models
class CommonResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")

class dementiaInfoRecord(BaseModel):
    dementiaKey : str = Field(examples=["123456"])
    dementiaName : str = Field(examples=["성춘향"])
    dementiaPhoneNumber : str = Field(examples=["010-1234-5678"])

class nokInfoRecord(BaseModel):
    nokKey : str = Field(examples=["123456"])
    nokName : str = Field(examples=["홍길동"])
    nokPhoneNumber : str = Field(examples=["010-1234-5678"])

class UserRecord(BaseModel):
    dementiaInfoRecord: dementiaInfoRecord
    nokInfoRecord: nokInfoRecord

class nokResult(BaseModel):
    dementiaInfoRecord: dementiaInfoRecord
    nokKey: str = Field(examples=["123456"])

class ReceiveNokInfoRequest(BaseModel):
    keyFromDementia : int = Field(examples=["123456"])
    nokName : str = Field(examples=["홍길동"])
    nokPhoneNumber : str = Field(examples=["010-1234-5678"])

class ReceiveNokInfoResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: nokResult


class dementiaResult(BaseModel):
    dementiaKey: str = Field(examples=["123456"])

class ReceiveDementiaInfoRequest(BaseModel):
    name : str = Field(examples=["성춘향"])
    phoneNumber : str = Field(examples=["010-1234-5678"])

class ReceiveDementiaInfoResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: dementiaResult


class connectionResult(BaseModel):
    nokInfoRecord: nokInfoRecord

class ConnectionRequest(BaseModel):
    dementiaKey : int = Field(examples=["123456"])

class ConnectionResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: connectionResult

class loginRequest(BaseModel):
    key : int = Field(examples=["123456"])
    isDementia : int = Field(examples=["1"], description="1 : 보호대상자, 0 : 보호자")

class ReceiveLocationRequest(BaseModel):
    dementiaKey : int = Field(examples=["123456"])
    date : str = Field(examples=["2024-03-19"], description="yyyy-mm-dd")
    time : str = Field(examples=["12:00:00"])
    latitude : float = Field(examples=["37.123456"])
    longitude : float = Field(examples=["127.123456"])
    bearing : float = Field(examples=["0.0"])
    accelerationSensor : List[float] = Field(..., examples=[[-1.84068, 6.68136, 6.0359]])
    gyroSensor : List[float] = Field(..., examples=[[-1.84068, 6.68136, 6.0359]])
    directionSensor : List[float] = Field(..., examples=[[-1.84068, 6.68136, 6.0359]])
    lightSensor : List[float] = Field(examples=[[500.0]])
    battery : int = Field(examples=["100"])
    isInternetOn : bool = Field(examples=["true"])
    isGpsOn : bool = Field(examples=["true"])
    isRingstoneOn : int = Field(examples=["1"])
    currentSpeed : float = Field(examples=["0.0"])

class LastLoc(BaseModel):
    latitude : float = Field(examples=["37.123456"])
    longitude : float = Field(examples=["127.123456"])
    bearing : float = Field(examples=["0.0"])
    currentSpeed : float = Field(examples=["0.0"])
    userStatus : int = Field(examples=["1"], description = " 1 : 정지, 2 : 도보, 3 : 차량, 4 : 지하철")
    battery : int = Field(examples=["100"])
    isInternetOn : bool = Field(examples=["true"])
    isGpsOn : bool = Field(examples=["true"])
    isRingstoneOn : int = Field(examples=["1"], description="2 : 벨소리,1 : 진동, 0 : 무음")

class GetLocationResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: LastLoc

class ModifyUserInfoRequest(BaseModel):
    key : int = Field(examples=["123456"])
    isDementia : int = Field(examples=["1"], description="1 : 보호대상자, 0 : 보호자")
    name : str = Field(examples=["김이름"])
    phoneNumber : str = Field(examples=["010-1234-5678"])

class ModifyUserUpdateRateRequest(BaseModel):
    key : int = Field(examples=["123456"])
    isDementia : int = Field(examples=["1"])
    updateRate : int = Field(examples=["15"], description="초 단위")

class AverageWalkingSpeedRequest(BaseModel):
    dementiaKey : int = Field(examples=["123456"])

class AverageAndLastLoc(BaseModel):
    averageSpeed : float = Field(examples=["2.0"])
    lastLatitude : float = Field(examples=["37.123456"])
    lastLongitude : float = Field(examples=["127.123456"])

class AverageWalkingSpeedResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: AverageAndLastLoc

class GetUserInfoResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: UserRecord

class MeaningfulLoc(BaseModel):
    dayOfTheWeek : str = Field(examples=["Monday"])
    time : str = Field(examples=["0408"], description="04 ~ 08")
    latitude : float
    longitude : float

class MeaningfulLocRecord(BaseModel):
    meaningfulLocations : List[MeaningfulLoc] = Field(..., examples=[{"dayOfTheWeek": "Monday", "time": "0408", "latitude": 37.123456, "longitude": 127.123456}])

class MeaningfulLocResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: MeaningfulLocRecord

class LocHis(BaseModel):
    latitude : float = Field(examples=["37.123456"])
    longitude : float = Field(examples=["127.123456"])
    time : str = Field(examples=["12:00:00"])

class LocHisRecord(BaseModel):
    locationHistory : List[LocHis]

class LocHistoryResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result : LocHisRecord

class ErrorResponse(BaseModel):
    status: str = Field("error")
    message: str = Field("에러 내용")

class TempResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result : int = Field("1", description="1(정지), 2(도보), 3(차량), 4(지하철)")