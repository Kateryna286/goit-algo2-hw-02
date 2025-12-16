from dataclasses import dataclass
from typing import List, Dict


@dataclass
class PrintJob:
    id: str
    volume: float
    priority: int
    print_time: int


@dataclass
class PrinterConstraints:
    max_volume: float
    max_items: int


def optimize_printing(print_jobs: List[Dict], constraints: Dict) -> Dict:
    """
    Оптимізує чергу 3D-друку згідно з пріоритетами та обмеженнями принтера

    Args:
        print_jobs: Список завдань на друк (dict)
        constraints: Обмеження принтера (dict)

    Returns:
        Dict з порядком друку та загальним часом
    """
    pc = PrinterConstraints(
        max_volume=constraints["max_volume"],
        max_items=constraints["max_items"],
    )

    if pc.max_items <= 0:
        raise ValueError("max_items must be > 0")
    if pc.max_volume <= 0:
        raise ValueError("max_volume must be > 0")

    jobs: List[PrintJob] = []
    for j in print_jobs:
        job = PrintJob(
            id=j["id"],
            volume=j["volume"],
            priority=j["priority"],
            print_time=j["print_time"],
        )

        if job.volume <= 0:
            raise ValueError(f"Job {job.id}: volume must be > 0")
        if job.print_time <= 0:
            raise ValueError(f"Job {job.id}: print_time must be > 0")
        if job.priority not in (1, 2, 3):
            raise ValueError(f"Job {job.id}: priority must be 1, 2, or 3")
        if job.volume > pc.max_volume:
            raise ValueError(
                f"Job {job.id}: volume {job.volume} exceeds printer max_volume {pc.max_volume}"
            )

        jobs.append(job)

    jobs_sorted = sorted(jobs, key=lambda x: x.priority)

    print_order: List[str] = []
    total_time = 0

    current_group: List[PrintJob] = []
    current_volume = 0.0
    current_max_time = 0

    def close_group():
        nonlocal total_time, current_group, current_volume, current_max_time
        if not current_group:
            return
        total_time += current_max_time
        current_group = []
        current_volume = 0.0
        current_max_time = 0

    for job in jobs_sorted:
        can_add_by_items = (len(current_group) + 1) <= pc.max_items
        can_add_by_volume = (current_volume + job.volume) <= pc.max_volume

        if not current_group:
            current_group.append(job)
            current_volume = job.volume
            current_max_time = job.print_time
            print_order.append(job.id)
            continue

        if can_add_by_items and can_add_by_volume:
            current_group.append(job)
            current_volume += job.volume
            current_max_time = max(current_max_time, job.print_time)
            print_order.append(job.id)
        else:
            close_group()
            current_group.append(job)
            current_volume = job.volume
            current_max_time = job.print_time
            print_order.append(job.id)

    close_group()

    return {
        "print_order": print_order,
        "total_time": total_time
    }


# Тестування
def test_printing_optimization():
    # Тест 1: Моделі однакового пріоритету
    test1_jobs = [
        {"id": "M1", "volume": 100, "priority": 1, "print_time": 120},
        {"id": "M2", "volume": 150, "priority": 1, "print_time": 90},
        {"id": "M3", "volume": 120, "priority": 1, "print_time": 150}
    ]

    # Тест 2: Моделі різних пріоритетів
    test2_jobs = [
        {"id": "M1", "volume": 100, "priority": 2, "print_time": 120},  # лабораторна
        {"id": "M2", "volume": 150, "priority": 1, "print_time": 90},   # дипломна
        {"id": "M3", "volume": 120, "priority": 3, "print_time": 150}   # особистий проєкт
    ]

    # Тест 3: Перевищення обмежень об'єму (не всі можна в одну групу)
    test3_jobs = [
        {"id": "M1", "volume": 250, "priority": 1, "print_time": 180},
        {"id": "M2", "volume": 200, "priority": 1, "print_time": 150},
        {"id": "M3", "volume": 180, "priority": 2, "print_time": 120}
    ]

    constraints = {
        "max_volume": 300,
        "max_items": 2
    }

    print("Тест 1 (однаковий пріоритет):")
    result1 = optimize_printing(test1_jobs, constraints)
    print(f"Порядок друку: {result1['print_order']}")
    print(f"Загальний час: {result1['total_time']} хвилин")
    assert result1["print_order"] == ["M1", "M2", "M3"]
    assert result1["total_time"] == 270

    print("\nТест 2 (різні пріоритети):")
    result2 = optimize_printing(test2_jobs, constraints)
    print(f"Порядок друку: {result2['print_order']}")
    print(f"Загальний час: {result2['total_time']} хвилин")
    assert result2["print_order"] == ["M2", "M1", "M3"]
    assert result2["total_time"] == 270

    print("\nТест 3 (перевищення обмежень):")
    result3 = optimize_printing(test3_jobs, constraints)
    print(f"Порядок друку: {result3['print_order']}")
    print(f"Загальний час: {result3['total_time']} хвилин")
    assert result3["print_order"] == ["M1", "M2", "M3"]
    assert result3["total_time"] == 450

    # Додатковий тест: завдання взагалі не можна надрукувати (об'єм > max_volume)
    print("\nДодатковий тест (неможливо надрукувати через об'єм):")
    impossible_jobs = [{"id": "X1", "volume": 999, "priority": 1, "print_time": 60}]
    try:
        optimize_printing(impossible_jobs, constraints)
        assert False, "Expected ValueError for job with volume > max_volume"
    except ValueError:
        print("Коректно: отримали ValueError")

    print("\nAll tests passed.")


if __name__ == "__main__":
    test_printing_optimization()
