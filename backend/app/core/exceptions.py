from fastapi import HTTPException, status


class FacialAnalysisException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class FaceNotDetectedException(FacialAnalysisException):
    def __init__(self, detail: str = "未检测到清晰人脸，请保持正面光线充足重新拍摄"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class FacePoseExtremeException(FacialAnalysisException):
    def __init__(self, detail: str = "面部偏转角度过大，请正视镜头平视拍摄"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class LLMServiceUnavailableException(FacialAnalysisException):
    def __init__(self, detail: str = "骨相分析算力暂时繁忙，请稍后重试"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
