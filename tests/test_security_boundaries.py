from agent.approval import ApprovalQueue


def test_approval_is_tenant_scoped():
    queue = ApprovalQueue()
    action = queue.enqueue("tenant-a", "calendar.create", {"title": "private"})

    assert queue.decide(action.id, "tenant-b", True) is None
    assert action.status == "pending"


def test_approval_cannot_be_replayed():
    queue = ApprovalQueue()
    action = queue.enqueue("tenant-a", "calendar.create", {})

    assert queue.decide(action.id, "tenant-a", True) is action
    assert queue.decide(action.id, "tenant-a", True) is None


def test_pending_list_is_tenant_scoped():
    queue = ApprovalQueue()
    first = queue.enqueue("tenant-a", "one", {})
    queue.enqueue("tenant-b", "two", {})

    assert queue.list_pending("tenant-a") == [first]
