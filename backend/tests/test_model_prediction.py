# backend/tests/test_model_prediction.py

from fastapi import status


# TEST INVALID REQUEST BODY
def test_invalid_request(client_with_mock_prediction):
    response = client_with_mock_prediction.post("/predict")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# TEST UNSUPPORTED FILE TYPE
def test_unsupported_file(client_with_mock_prediction, unsupported_file_type):
    response = client_with_mock_prediction.post(
        "/predict",
        files={"audio_file": ("clip.wav", unsupported_file_type, "audio/gg")},
    )
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


# TEST WRONG CONTENT-TYPE IN REQUEST
def test_wrong_content_type(client_with_mock_prediction, valid_wav_bytes):
    response = client_with_mock_prediction.post(
        "/predict",
        files={"audio_file": ("clip", valid_wav_bytes, "application/json")},
    )
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


# TEST CORRUPT FILE UPLOAD
def test_corrupt_upload(client_with_mock_prediction, corrupt_audio_bytes):
    response = client_with_mock_prediction.post(
        "/predict",
        files={"audio_file": ("clip.wav", corrupt_audio_bytes, "audio/wav")},
    )
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


# TEST EMPTY FILE UPLOAD
def test_empty_upload(client_with_mock_prediction, empty_audio_bytes):
    response = client_with_mock_prediction.post(
        "/predict", files={"audio_file": ("clip.wav", empty_audio_bytes, "audio/wav")}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# TEST SUCCESSFUL FILE UPLOAD
def test_file_upload_success(client_with_mock_prediction, valid_wav_bytes):
    response = client_with_mock_prediction.post(
        "/predict", files={"audio_file": ("clip.wav", valid_wav_bytes, "audio/wav")}
    )

    assert response.status_code == status.HTTP_200_OK
