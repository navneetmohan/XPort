from app.core.tasks import health_check_task


def test_health_check_task_execution():
    """Verify that health_check_task executes properly."""
    result = health_check_task.apply()
    assert result.successful()
    payload = result.result
    assert payload["status"] == "ok"
    assert payload["task"] == "health_check_task"
    assert "operational" in payload["message"]
