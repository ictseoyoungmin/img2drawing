from contextlib import contextmanager

@contextmanager
def drawing_transaction(session, *, label="transaction"):
    tx=session.transaction(label=label)
    try:
        yield tx
        tx.commit()
    except Exception:
        tx.rollback()
        raise
