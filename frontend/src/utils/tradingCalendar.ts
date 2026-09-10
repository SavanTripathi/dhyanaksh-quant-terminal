// NSE Official Holidays 2026
const NSE_HOLIDAYS_2026: Set<string> = new Set([
  '2026-01-26', // Republic Day
  '2026-03-10', // Maha Shivratri
  '2026-03-25', // Holi
  '2026-04-02', // Good Friday
  '2026-04-14', // Dr. Ambedkar Jayanti
  '2026-05-01', // Maharashtra Day
  '2026-08-15', // Independence Day
  '2026-10-02', // Mahatma Gandhi Jayanti
  '2026-10-20', // Dussehra
  '2026-11-10', // Diwali
  '2026-12-25', // Christmas
]);

/**
 * Returns the latest finalized NSE trading day (YYYY-MM-DD).
 * - Market closes at 15:30 IST; official settlement prices are fully finalized by 16:00 IST.
 * - If before 16:00 IST on an active weekday, steps back to the prior completed session.
 * - If weekend (Saturday/Sunday) or official holiday, steps back until a completed trading day is reached.
 */
export function getLastCompletedTradingDay(refDate?: Date): string {
  const now = refDate ? new Date(refDate) : new Date();
  
  // Calculate current date/time in IST (UTC + 5:30)
  const utcMs = now.getTime() + now.getTimezoneOffset() * 60000;
  const istDate = new Date(utcMs + 5.5 * 3600000);

  // If before 16:00 IST, today's trading session is not yet finalized
  if (istDate.getHours() < 16) {
    istDate.setDate(istDate.getDate() - 1);
  }

  // Iterate backward to find the latest valid weekday not in holidays
  for (let i = 0; i < 30; i++) {
    const day = istDate.getDay(); // 0 = Sun, 6 = Sat
    const yyyy = istDate.getFullYear();
    const mm = String(istDate.getMonth() + 1).padStart(2, '0');
    const dd = String(istDate.getDate()).padStart(2, '0');
    const dateStr = `${yyyy}-${mm}-${dd}`;

    if (day !== 0 && day !== 6 && !NSE_HOLIDAYS_2026.has(dateStr)) {
      return dateStr;
    }
    istDate.setDate(istDate.getDate() - 1);
  }

  return '2026-09-09';
}
