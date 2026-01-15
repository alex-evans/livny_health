import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui';
import { getDailySchedule } from '../api';
import { cn } from '../utils/cn';
import type { User, DailySchedule, Appointment, AppointmentStatus } from '../types';

function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatDisplayDate(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function formatTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

function calculateAge(dateOfBirth: string): number {
  const today = new Date();
  const birth = new Date(dateOfBirth);
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}

function isToday(dateStr: string): boolean {
  return dateStr === formatDate(new Date());
}

function getNextAppointmentIndex(appointments: Appointment[]): number {
  const now = new Date();
  for (let i = 0; i < appointments.length; i++) {
    const appt = appointments[i];
    if (appt.status === 'scheduled' || appt.status === 'checked_in') {
      const apptTime = new Date(appt.appointmentTime);
      if (apptTime > now) {
        return i;
      }
    }
    if (appt.status === 'in_progress') {
      return i;
    }
  }
  return -1;
}

interface StatusBadgeProps {
  status: AppointmentStatus;
}

function StatusBadge({ status }: StatusBadgeProps) {
  const styles: Record<AppointmentStatus, string> = {
    scheduled: 'bg-arctic text-deep-ice',
    checked_in: 'bg-[#E8F6EF] text-success',
    in_progress: 'bg-glacier-blue text-white',
    completed: 'bg-frost text-text-tertiary',
    no_show: 'bg-[#FEF5E7] text-warning',
    canceled: 'bg-[#FADBD8] text-critical',
  };

  const labels: Record<AppointmentStatus, string> = {
    scheduled: 'Scheduled',
    checked_in: 'Checked In',
    in_progress: 'In Progress',
    completed: 'Completed',
    no_show: 'No Show',
    canceled: 'Canceled',
  };

  return (
    <span className={cn('text-[11px] font-medium uppercase tracking-wide px-2 py-1 rounded', styles[status])}>
      {labels[status]}
    </span>
  );
}

interface VisitTypeBadgeProps {
  visitType: string;
}

function VisitTypeBadge({ visitType }: VisitTypeBadgeProps) {
  const isUrgent = visitType === 'Urgent';
  return (
    <span
      className={cn(
        'text-[11px] font-medium px-2 py-1 rounded',
        isUrgent ? 'bg-[#FEF5E7] text-warning' : 'bg-arctic text-deep-ice'
      )}
    >
      {visitType}
    </span>
  );
}

interface AppointmentCardProps {
  appointment: Appointment;
  isNext: boolean;
  isCurrent: boolean;
  onSelect: (patientId: string) => void;
}

function AppointmentCard({ appointment, isNext, isCurrent, onSelect }: AppointmentCardProps) {
  const isPast = appointment.status === 'completed' || appointment.status === 'no_show';
  const isCanceled = appointment.status === 'canceled';
  const age = calculateAge(appointment.patient.dateOfBirth);

  return (
    <Card
      hoverable={!isCanceled}
      onClick={isCanceled ? undefined : () => onSelect(appointment.patient.id)}
      className={cn(
        'relative',
        isPast && 'opacity-60',
        isCanceled && 'opacity-50 cursor-not-allowed',
        isCurrent && 'ring-2 ring-glacier-blue',
        isNext && !isCurrent && 'ring-2 ring-success'
      )}
    >
      {isNext && !isCurrent && (
        <div className="absolute -top-2 -right-2 bg-success text-white text-[11px] font-medium uppercase tracking-wide px-2 py-1 rounded">
          Up Next
        </div>
      )}
      {appointment.isDoubleBooked && (
        <div className="absolute -top-2 -left-2 bg-warning text-white text-[11px] font-medium px-2 py-1 rounded">
          Double Booked
        </div>
      )}

      <div className="flex items-start gap-comfortable">
        {/* Time Column */}
        <div className="w-20 flex-shrink-0">
          <p className="text-[15px] font-semibold text-text-primary">
            {formatTime(appointment.appointmentTime)}
          </p>
          <p className="text-[13px] text-text-tertiary">{appointment.durationMinutes} min</p>
        </div>

        {/* Patient Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-tight flex-wrap">
            <h3 className="text-[15px] font-semibold text-text-primary">
              {appointment.patient.name}
            </h3>
            <span className="text-[13px] text-text-secondary">
              {age}y {appointment.patient.gender.charAt(0)}
            </span>
          </div>

          {appointment.chiefComplaint && (
            <p className="text-[13px] text-text-secondary italic mt-1 truncate">
              {appointment.chiefComplaint}
            </p>
          )}

          {/* Flags */}
          {appointment.flags.length > 0 && (
            <div className="flex flex-wrap gap-tight mt-2">
              {appointment.flags.map((flag, idx) => (
                <span
                  key={idx}
                  className={cn(
                    'text-[11px] px-2 py-1 rounded',
                    flag.type === 'critical_lab' && 'bg-[#FADBD8] text-critical',
                    flag.type === 'overdue_screening' && 'bg-[#FEF5E7] text-warning',
                    flag.type === 'special_needs' && 'bg-arctic text-deep-ice',
                    flag.type === 'new_patient' && 'bg-[#E8F6EF] text-success'
                  )}
                >
                  {flag.message}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Badges */}
        <div className="flex flex-col items-end gap-tight flex-shrink-0">
          <StatusBadge status={appointment.status} />
          <VisitTypeBadge visitType={appointment.visitType} />
        </div>
      </div>
    </Card>
  );
}

export function DailySchedulePage() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(formatDate(new Date()));
  const [schedule, setSchedule] = useState<DailySchedule | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const userJson = sessionStorage.getItem('currentUser');
    if (userJson) {
      setCurrentUser(JSON.parse(userJson));
    } else {
      navigate('/login');
    }
  }, [navigate]);

  const fetchSchedule = useCallback(async (date: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDailySchedule(date);
      setSchedule(data);
    } catch (err) {
      setError('Failed to load schedule');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSchedule(selectedDate);
  }, [selectedDate, fetchSchedule]);

  // Poll for real-time updates every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (!loading) {
        fetchSchedule(selectedDate);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [selectedDate, loading, fetchSchedule]);

  const handlePreviousDay = () => {
    const date = new Date(selectedDate + 'T00:00:00');
    date.setDate(date.getDate() - 1);
    setSelectedDate(formatDate(date));
  };

  const handleNextDay = () => {
    const date = new Date(selectedDate + 'T00:00:00');
    date.setDate(date.getDate() + 1);
    setSelectedDate(formatDate(date));
  };

  const handleToday = () => {
    setSelectedDate(formatDate(new Date()));
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedDate(e.target.value);
  };

  const handlePatientSelect = (patientId: string) => {
    navigate(`/patients/${patientId}`);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('currentUser');
    navigate('/login');
  };

  const handleGoToPatients = () => {
    navigate('/patients');
  };

  if (!currentUser) {
    return null;
  }

  const appointments = schedule?.appointments ?? [];
  const nextAppointmentIndex = isToday(selectedDate) ? getNextAppointmentIndex(appointments) : -1;

  // Find current in-progress appointment
  const currentAppointmentIndex = appointments.findIndex((a) => a.status === 'in_progress');

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent, idx: number) => {
    if (e.key === 'ArrowDown' && idx < appointments.length - 1) {
      const nextCard = document.querySelector(`[data-appointment-index="${idx + 1}"]`) as HTMLElement;
      nextCard?.focus();
    } else if (e.key === 'ArrowUp' && idx > 0) {
      const prevCard = document.querySelector(`[data-appointment-index="${idx - 1}"]`) as HTMLElement;
      prevCard?.focus();
    } else if (e.key === 'Enter') {
      const appt = appointments[idx];
      if (appt.status !== 'canceled') {
        handlePatientSelect(appt.patient.id);
      }
    }
  };

  return (
    <div className="min-h-screen bg-snow">
      <header className="bg-white shadow-card">
        <div className="max-w-5xl mx-auto px-generous py-normal flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-deep-ice">Schedule</h1>
            <p className="text-[13px] text-text-tertiary">
              {schedule?.providerName ?? currentUser.name}
            </p>
          </div>
          <div className="flex items-center gap-normal">
            <button
              onClick={handleGoToPatients}
              className="text-[15px] text-glacier-blue hover:text-deep-ice transition-colors"
            >
              Patients
            </button>
            <button
              onClick={handleLogout}
              className="text-[15px] text-text-secondary hover:text-text-primary transition-colors"
            >
              Switch User
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-generous py-generous">
        {/* Date Navigation */}
        <div className="flex items-center justify-between mb-generous">
          <div className="flex items-center gap-normal">
            <button
              onClick={handlePreviousDay}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-frost rounded transition-colors"
              aria-label="Previous day"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <h2 className="text-lg font-semibold text-text-primary min-w-[280px] text-center">
              {formatDisplayDate(selectedDate)}
            </h2>

            <button
              onClick={handleNextDay}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-frost rounded transition-colors"
              aria-label="Next day"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <div className="flex items-center gap-normal">
            {!isToday(selectedDate) && (
              <button
                onClick={handleToday}
                className="text-[15px] text-glacier-blue hover:text-deep-ice transition-colors"
              >
                Today
              </button>
            )}
            <input
              type="date"
              value={selectedDate}
              onChange={handleDateChange}
              className="bg-white border border-arctic rounded-md px-3 py-2 text-[15px] text-text-primary focus:outline-none focus:border-glacier-blue focus:ring-[3px] focus:ring-glacier-blue/10"
            />
          </div>
        </div>

        {/* Schedule Summary */}
        {!loading && !error && schedule && (
          <div className="flex items-center gap-comfortable mb-normal text-[13px] text-text-secondary">
            <span>
              {appointments.filter((a) => a.status !== 'canceled').length} appointments
            </span>
            <span className="text-text-tertiary">|</span>
            <span>
              {appointments.filter((a) => a.status === 'completed').length} completed
            </span>
            {appointments.some((a) => a.status === 'no_show') && (
              <>
                <span className="text-text-tertiary">|</span>
                <span className="text-warning">
                  {appointments.filter((a) => a.status === 'no_show').length} no-show
                </span>
              </>
            )}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-section">
            <div className="w-8 h-8 border-2 border-glacier-blue border-t-transparent rounded-full animate-spin mb-normal" />
            <p className="text-[15px] text-text-secondary">Loading schedule...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <Card className="border-l-4 border-l-critical">
            <p className="text-[15px] text-critical">{error}</p>
            <button
              onClick={() => fetchSchedule(selectedDate)}
              className="text-[15px] text-glacier-blue hover:text-deep-ice mt-2"
            >
              Try again
            </button>
          </Card>
        )}

        {/* Empty State */}
        {!loading && !error && appointments.length === 0 && (
          <Card>
            <div className="text-center py-generous">
              <p className="text-[15px] text-text-secondary">
                No appointments scheduled for this day
              </p>
            </div>
          </Card>
        )}

        {/* Appointments List */}
        {!loading && !error && appointments.length > 0 && (
          <div className="flex flex-col gap-normal">
            {appointments.map((appointment, idx) => (
              <div
                key={appointment.id}
                data-appointment-index={idx}
                tabIndex={0}
                onKeyDown={(e) => handleKeyDown(e, idx)}
                className="focus:outline-none focus:ring-2 focus:ring-glacier-blue rounded-lg"
              >
                <AppointmentCard
                  appointment={appointment}
                  isNext={idx === nextAppointmentIndex}
                  isCurrent={idx === currentAppointmentIndex}
                  onSelect={handlePatientSelect}
                />
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
