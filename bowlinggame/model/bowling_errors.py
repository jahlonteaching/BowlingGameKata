class BowlingError(Exception):
    pass


class FramePinsExceededError(BowlingError):
    """
    Raised when the number of pins in a frame exceeds 10
    """
    pass

class ExtraRollWithOpenFrameError(BowlingError):
    """
    Raised when an extra roll is added to an open frame
    """
    pass

class TenthFrameWithMoreThanThreeRollsError(BowlingError):
    """
    Raised when a tenth frame has more than three rolls
    """
    pass