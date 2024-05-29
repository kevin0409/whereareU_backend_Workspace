from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# Define request and response models
'''class accessToken(BaseModel):
    accessToken: str = Field(examples=["ksjdnfjkdasnfljsknafljansdfjlsakn"])

class CommonResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result : accessToken'''

class CommonResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")

class dementiaInfoRecord(BaseModel):
    dementiaKey : str = Field(examples=["123456"])
    dementiaName : str = Field(examples=["성춘향"])
    dementiaPhoneNumber : str = Field(examples=["010-1234-5678"])
    updateRate : int = Field(examples=["15"], description="초 단위")

class nokInfoRecord(BaseModel):
    nokKey : str = Field(examples=["123456"])
    nokName : str = Field(examples=["홍길동"])
    nokPhoneNumber : str = Field(examples=["010-1234-5678"])
    updateRate : int = Field(examples=["15"], description="초 단위")

class UserRecord(BaseModel):
    dementiaInfoRecord: dementiaInfoRecord
    nokInfoRecord: nokInfoRecord

class nokResult(BaseModel):
    dementiaInfoRecord: dementiaInfoRecord
    nokKey: str = Field(examples=["123456"])
    #accessToken: str = Field(examples=["ksjdnfjkdasnfljsknafljansdfjlsakn"])
    #refreshToken: str = Field(examples=["ksjdnfjkdasnfljsknafljansdfjlsakn"])

class ReceiveNokInfoRequest(BaseModel):
    keyFromDementia : int = Field(examples=["123456"])
    nokName : str = Field(examples=["홍길동"])
    nokPhoneNumber : str = Field(examples=["010-1234-5678"])
    fcmToken : str = Field(examples=["ksjdnfjkdasnfljsknafljansdfjlsakn"])

class ReceiveNokInfoResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: nokResult


class dementiaResult(BaseModel):
    dementiaKey: str = Field(examples=["123456"])

class ReceiveDementiaInfoRequest(BaseModel):
    name : str = Field(examples=["성춘향"])
    phoneNumber : str = Field(examples=["010-1234-5678"])
    fcmToken : str = Field(examples=["ksjdnfjkdasnfljsknafljansdfjlsakn"])

class ReceiveDementiaInfoResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: dementiaResult

class connectionResult(BaseModel):
    nokInfoRecord: nokInfoRecord
    #accessToken: str = Field(examples=["ksjdnfjkdasnfljsknafljansdfjlsakn"])
    #refreshToken: str = Field(examples=["ksjdnfjkdasnfljsknafljansdfjlsakn"])

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
    dementiaKey : str = Field(examples=["123456"])
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
    key: str = Field(examples=["123456"])
    isDementia : int = Field(examples=[1], description="1 : 보호대상자, 0 : 보호자")
    name : str = Field(examples=["김이름"])
    phoneNumber : str = Field(examples=["010-1234-5678"])

class ModifyUserUpdateRateRequest(BaseModel):
    key: str = Field(examples=["123456"])
    isDementia : int = Field(examples=[1], description="1 : 보호대상자, 0 : 보호자")
    updateRate : int = Field(examples=[1], description="분 단위")

class AverageAndLastLoc(BaseModel):
    averageSpeed : float = Field(examples=["2.0"])
    lastLatitude : float = Field(examples=["37.123456"])
    lastLongitude : float = Field(examples=["127.123456"])
    addressName : str = Field(examples=["서울특별시 강남구 니가 사는 그 집"])

class AverageWalkingSpeedResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: AverageAndLastLoc

class GetUserInfoResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: UserRecord

class timeInfoList(BaseModel):
    dayOfTheWeek : str = Field(examples=["월요일"])
    time : str = Field(examples=["0408"])

class PoliceStationInfoList(BaseModel):
    policeName : str = Field(examples=["서울동작경찰서"])
    policePhoneNumber : str = Field(examples=["02-1234-5678"])
    policeAddress : str = Field(examples=["서울 동작구 노량진동 72-35"])
    roadAddress : str = Field(examples=["서울 동작구 노량진로 148"])
    distance : int = Field(examples=["2005"], description="미터 단위")
    latitude : float = Field(examples=["37.123456"])
    longitude : float = Field(examples=["127.123456"])


class MeaningfulLoc(BaseModel):
    address : str = Field(examples=["서울특별시 강남구 니가 사는 그 집"])
    timeInfo : timeInfoList
    latitude : float = Field(examples=["37.123456"])
    longitude : float = Field(examples=["127.123456"])
    policeStationInfo : List[PoliceStationInfoList]

class MeaningfulLocRecord(BaseModel):
    meaningfulLocations : List[MeaningfulLoc]

class MeaningfulLocResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: MeaningfulLocRecord

class LocHis(BaseModel):
    latitude : float = Field(examples=["37.123456"])
    longitude : float = Field(examples=["127.123456"])
    time : str = Field(examples=["12:00:00 or 12:00:00,12:01:00"], description='정지 일땐 시작, 끝 시간임')
    userStatus : int = Field(examples=["1"], description = " 1 : 정지, 2 : 도보, 3 : 차량, 4 : 지하철")
    distance : int = Field(examples=["2005"], description="미터 단위(소수점 2자리까지)")

class LocHisRecord(BaseModel):
    locationHistory : List[LocHis]

class LocHistoryResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result : LocHisRecord

class ErrorResponse(BaseModel):
    detail: str = Field("에러 내용")

class TempResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result : int = Field("1", description="1(정지), 2(도보), 3(차량), 4(지하철)")

class Token(BaseModel):
    accessToken: str = Field("ksjdnfjkdasnfljsknafljansdfjlsakn")
    refreshToken: str = Field("ksjdnfjkdasnfljsknafljansdfjlsakn")
    tokenType: str = Field("bearer")

class TokenResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result : List[Token]

class predloc(BaseModel):
    latitude : float = Field(examples=["37.123456"])
    longitude : float = Field(examples=["127.123456"])
    address : str = Field(examples=["서울특별시 강남구 니가 사는 그 집"])

class locpredict(BaseModel):
    predictLocation : predloc
    policeInfo : PoliceStationInfoList

class PredictLocationResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result : locpredict

class AverageWalkingSpeedRequest(BaseModel):
    dementiaKey : str = Field(examples=["123456"])

class AverageAndLastLoc(BaseModel):
    averageSpeed : float = Field(examples=["2.0"])
    lastLatitude : float = Field(examples=["37.123456"])
    lastLongitude : float = Field(examples=["127.123456"])
    addressName : str = Field(examples=["서울특별시 강남구 니가 사는 그 집"])

class AverageWalkingSpeedResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: AverageAndLastLoc

class RegisterSafeAreaRequest(BaseModel):
    dementiaKey : str = Field(examples=["123456"])
    groupName : str = Field(examples=["안심구역 그룹 1"])
    areaName : str = Field(examples=["집"])
    latitude : float = Field(examples=["37.123456"])
    longitude : float = Field(examples=["127.123456"])
    radius : int = Field(examples=["100"], description="미터 단위")

class safeAreaList(BaseModel):
    areaName : str = Field(examples=["집"])
    areaKey : str = Field(examples=["123456"])
    latitude : float = Field(examples=["37.123456"])
    longitude : float = Field(examples=["127.123456"])
    radius : int = Field(examples=["100"], description="미터 단위")

class safeAreaGroupInfo(BaseModel):
    groupName : str = Field(examples=["안심구역 그룹 1"])
    groupKey : str = Field(examples=["123456"])
    safeAreas : List[safeAreaList]


class GetSafeAreaResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: List[safeAreaGroupInfo]

class ModifySafeAreaName(BaseModel):
    dementiaKey : str = Field(examples=["123456"])
    areaKey : str = Field(examples=["123456"])
    afterAreaName : Optional[str] = Field(examples=["집2"])

class ModifySafeAreaGroup(BaseModel):
    dementiaKey : str = Field(examples=["123456"])
    areaKey : str = Field(examples=["123456"])
    groupKey : str = Field(examples=["123456"])

class safeAreaGruop(BaseModel):
    safeAreas : List[safeAreaList]

class GetSafeAreaGroupResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: safeAreaGruop

class ModifySafeAreaGroupName(BaseModel):
    dementiaKey : str = Field(examples=["123456"])
    groupKey : str = Field(examples=["123456"])
    afterGroupName : Optional[str] = Field(examples=["안심구역 그룹 2"])

class DeleteSafeAreaRequest(BaseModel):
    dementiaKey : str = Field(examples=["123456"])
    areaKey : str = Field(examples=["123456"])

class DeleteSafeAreaGroupRequest(BaseModel):
    dementiaKey : str = Field(examples=["123456"])
    groupKey : str = Field(examples=["123456"])

class FCMRequest(BaseModel):
    token : str = Field(examples=["ksjdnfjkdasnfljsknafljansdfjlsakn"])
    title : str = Field(examples=["어디U"])
    body : str = Field(examples=["안심 구역 진입"])
    data : Dict[str, str] = Field(examples=[{"safeAreaName" : "집", "time" : "12:00:00"}])


class AddressConversionRequest(BaseModel):
    address : str = Field(examples=["서울특별시 강남구 니가 사는 그 집"])

class latilongi(BaseModel):
    latitude : float = Field(examples=["37.123456"])
    longitude : float = Field(examples=["127.123456"])

class AddressConversionResponse(BaseModel):
    status: str = Field("success")
    message: str = Field("메~시~지~")
    result: Dict[str, float] = latilongi