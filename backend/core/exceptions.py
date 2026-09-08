# backend/core/exceptions.py


class AudioProcessingError(Exception):
    pass


class AudioDecodingTimeOutError(AudioProcessingError):
    pass


class UnsupportedAudioError(AudioProcessingError):
    pass


class DecoderUnavailableError(AudioProcessingError):
    pass


class EmptyAudioError(AudioProcessingError):
    pass


class AudioUploadSizeError(AudioProcessingError):
    pass


class AudioReadError(AudioProcessingError):
    pass


class RetrievalError(Exception):
    pass


class InferenceError(Exception):
    pass
