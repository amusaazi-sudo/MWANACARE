"""Works out what a child needs next, for the Home screen."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class ChildOverview:
    given: int = 0
    total: int = 0
    next_due: date | None = None
    next_records: list = field(default_factory=list)  # vaccines due on the same next date
    coming_up: list = field(default_factory=list)     # the few after that
    days_until: int | None = None                      # negative when overdue

    @property
    def percent(self):
        return round(100 * self.given / self.total) if self.total else 0

    @property
    def is_overdue(self):
        return self.days_until is not None and self.days_until < 0

    @property
    def days_late(self):
        return -self.days_until if self.is_overdue else 0


def child_overview(child, today=None):
    today = today or date.today()
    records = list(child.immunizationrecord_set.all())
    pending = sorted(
        (r for r in records if not r.date_given and r.next_due_date),
        key=lambda r: r.next_due_date,
    )
    overview = ChildOverview(given=sum(1 for r in records if r.date_given), total=len(records))
    if pending:
        overview.next_due = pending[0].next_due_date
        overview.next_records = [r for r in pending if r.next_due_date == overview.next_due]
        overview.coming_up = pending[len(overview.next_records):len(overview.next_records) + 3]
        overview.days_until = (overview.next_due - today).days
    return overview


@dataclass
class CardRow:
    """One row on the vaccination card: vaccines given (or due) on the same date."""

    state: str            # "done", "late", "due", "later" or "unscheduled"
    when: date | None
    records: list
    facility: object = None


STATE_FOR_STATUS = {"Completed": "done", "Overdue": "late", "Due soon": "due", "Upcoming": "later"}
STATE_ORDER = ["done", "late", "due", "later", "unscheduled"]


def vaccination_card(records):
    """Group records into card rows, oldest first, like stamps in a paper health card."""
    rows = {}
    for record in records:
        state = STATE_FOR_STATUS[record.status]
        when = record.date_given or record.next_due_date
        if when is None:
            state = "unscheduled"
        row = rows.setdefault((state, when), CardRow(state=state, when=when, records=[]))
        row.records.append(record)
        row.facility = row.facility or record.facility
    return sorted(rows.values(), key=lambda r: (STATE_ORDER.index(r.state), r.when or date.max))
