class StaleReviewError(RuntimeError):
    pass

def assert_review_artifact_current(artifacts, *, current_state_sha256: str, current_cursor: int) -> None:
    drawing = artifacts.drawing
    if drawing.state_sha256 != current_state_sha256 or drawing.history_cursor != int(current_cursor):
        raise StaleReviewError("review is stale: drawing changed after review artifact was prepared")

def assert_review_current(review, *, current_state_sha256: str, current_cursor: int) -> None:
    if review.drawing_state_sha256 != current_state_sha256 or review.history_cursor != int(current_cursor):
        raise StaleReviewError("review is stale: drawing changed after review artifact was prepared")
def assert_local_review_current(local_review, *, current_state_sha256: str, current_cursor: int) -> None:
    if (
        local_review.drawing_state_sha256 != current_state_sha256
        or local_review.history_cursor != int(current_cursor)
    ):
        raise StaleReviewError(
            "local review is stale: drawing changed after the local crop artifacts were prepared"
        )
