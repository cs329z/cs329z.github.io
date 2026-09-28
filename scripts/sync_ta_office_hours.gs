/**
 * Sync CS329Z TA office hours to the public course Google Calendar.
 *
 * First run previewTaOfficeHours() and inspect the execution log. Then run
 * syncTaOfficeHours(); Google will request Calendar authorization once.
 */
const CALENDAR_ID =
  '59a6e4ad6abfe74cf389924dd1a5f8a9c7358ee32c2c7db1fd49d6ce4d252de1@group.calendar.google.com';
const TIME_ZONE = 'America/Los_Angeles';
const TERM_START = '2026-09-28';
const TERM_END_EXCLUSIVE = '2026-12-05';
const EVENT_MARKER = '[cs329z-ta-office-hours-v1]';

const TA_OFFICE_HOURS = [
  {name: 'Shreyas Sharma', weekday: 1, start: '16:30', end: '17:30', location: 'CoDA Basement'},
  {name: 'Anusheh Chaudry', weekday: 2, start: '13:30', end: '14:30', location: 'CoDA Basement'},
  {name: 'Houjun Liu', weekday: 3, start: '09:30', end: '10:30', location: 'Durand 218'},
  {name: 'Owen Queen', weekday: 5, start: '10:30', end: '11:30', location: 'Packard 339'},
];

const NO_OFFICE_HOURS = new Set([
  '2026-11-23',
  '2026-11-24',
  '2026-11-25',
  '2026-11-26',
  '2026-11-27',
]);

function plannedTaOfficeHours() {
  const events = [];
  const first = new Date(`${TERM_START}T12:00:00Z`);
  const end = new Date(`${TERM_END_EXCLUSIVE}T12:00:00Z`);

  for (let cursor = new Date(first); cursor < end; cursor.setUTCDate(cursor.getUTCDate() + 1)) {
    const date = Utilities.formatDate(cursor, 'UTC', 'yyyy-MM-dd');
    if (NO_OFFICE_HOURS.has(date)) continue;

    for (const officeHour of TA_OFFICE_HOURS) {
      if (cursor.getUTCDay() !== officeHour.weekday) continue;
      events.push({
        title: `CS329Z Office Hours — ${officeHour.name}`,
        start: parseCourseTime_(date, officeHour.start),
        end: parseCourseTime_(date, officeHour.end),
        location: officeHour.location,
      });
    }
  }
  return events;
}

function previewTaOfficeHours() {
  for (const event of plannedTaOfficeHours()) {
    const start = Utilities.formatDate(event.start, TIME_ZONE, 'EEE, MMM d, h:mm a');
    const end = Utilities.formatDate(event.end, TIME_ZONE, 'h:mm a');
    console.log(`${start}–${end}: ${event.title} (${event.location})`);
  }
}

function syncTaOfficeHours() {
  const calendar = CalendarApp.getCalendarById(CALENDAR_ID);
  if (!calendar) throw new Error(`Calendar not found or not writable: ${CALENDAR_ID}`);

  const windowStart = parseCourseTime_(TERM_START, '00:00');
  const windowEnd = parseCourseTime_(TERM_END_EXCLUSIVE, '00:00');
  let deleted = 0;
  for (const event of calendar.getEvents(windowStart, windowEnd)) {
    if (event.getDescription().includes(EVENT_MARKER)) {
      event.deleteEvent();
      deleted += 1;
    }
  }

  const description =
    `${EVENT_MARKER}\nOffice-hours schedule: ` +
    'https://cs329z.stanford.edu/logistics.html#office-hours';
  const events = plannedTaOfficeHours();
  for (const event of events) {
    calendar.createEvent(event.title, event.start, event.end, {
      description,
      location: event.location,
    });
  }
  console.log(`Deleted ${deleted} prior TA events; created ${events.length} events.`);
}

function parseCourseTime_(date, time) {
  return Utilities.parseDate(`${date} ${time}`, TIME_ZONE, 'yyyy-MM-dd HH:mm');
}
