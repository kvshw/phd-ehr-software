/**
 * Appointment Sidebar Component
 * Shows doctor appointments, calendar, and today's patients
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
// Removed unused import

interface AppointmentSidebarProps {
  todayPatients?: Array<{
    id: string;
    name: string;
    age: number;
    time: string;
    avatar?: string;
  }>;
}

export function AppointmentSidebar({ todayPatients = [] }: AppointmentSidebarProps) {
  const router = useRouter();
  const [selectedDate, setSelectedDate] = useState(9);
  const [selectedTimeSlot, setSelectedTimeSlot] = useState('11.00 AM - 12.00 PM');

  // Generate calendar days
  const days = Array.from({ length: 31 }, (_, i) => i + 1);
  const availableDates = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31];
  const fullBookedDates = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30];

  const timeSlots = [
    '10.00 AM - 11.00 AM',
    '11.00 AM - 12.00 PM',
    '01.00 PM - 02.00 PM',
  ];

  const getDateStatus = (day: number) => {
    if (availableDates.includes(day)) return 'available';
    if (fullBookedDates.includes(day)) return 'full';
    return 'unavailable';
  };

  return (
    <aside className="w-80 bg-white rounded-2xl shadow border border-gray-200 p-6 space-y-6 h-fit sticky top-24">
      {/* Doctor's Appointment Section */}
      <div>
        <div className="mb-4">
          <h2 className="text-lg font-bold text-gray-900">Doctor's appointment</h2>
          <p className="text-sm text-gray-500">prepared to discuss with doctor</p>
        </div>

        {/* Calendar */}
        <div className="mb-6">
          <p className="text-xs font-semibold text-gray-700 mb-3">Available date to consultations</p>
          <div className="grid grid-cols-7 gap-2">
            {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day, index) => (
              <div key={index} className="text-center text-xs font-semibold text-gray-500 py-1">
                {day}
              </div>
            ))}
            {days.map((day) => {
              const status = getDateStatus(day);
              const isSelected = selectedDate === day;
              return (
                <button
                  key={day}
                  onClick={() => setSelectedDate(day)}
                  className={`relative h-8 w-8 rounded-lg text-xs font-medium transition-all ${
                    isSelected
                      ? 'bg-blue-600 text-white shadow scale-110'
                      : status === 'available'
                      ? 'bg-blue-50 text-blue-600 hover:bg-blue-100'
                      : status === 'full'
                      ? 'bg-gray-200 text-gray-500'
                      : 'bg-gray-50 text-gray-400'
                  }`}
                >
                  {day}
                  {isSelected && (
                    <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-blue-600 rounded-full"></div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Time Slots Popup */}
          {selectedDate && (
            <div className="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-200">
              <p className="text-xs font-semibold text-gray-700 mb-2">Available times:</p>
              <div className="space-y-2">
                {timeSlots.map((slot) => (
                  <button
                    key={slot}
                    onClick={() => setSelectedTimeSlot(slot)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                      selectedTimeSlot === slot
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-blue-100'
                    }`}
                  >
                    {selectedTimeSlot === slot && '✓ '}
                    {slot}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Legend */}
          <div className="mt-4 flex flex-wrap gap-3 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              <span className="text-gray-600">Available</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-gray-400"></div>
              <span className="text-gray-600">Full booked</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-gray-200"></div>
              <span className="text-gray-600">Not Available</span>
            </div>
          </div>
        </div>

        {/* Doctor Info */}
        <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-semibold shadow">
              AP
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900">Dr. Arcadius Phina</p>
              <p className="text-xs text-gray-600">Orthopedic doctor</p>
            </div>
            <button className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Today's Patients */}
      <div>
        <h3 className="text-sm font-bold text-gray-900 mb-4">Our patient today</h3>
        <div className="space-y-3">
          {todayPatients.length > 0 ? (
            todayPatients.map((patient) => (
              <div
                key={patient.id}
                onClick={() => router.push(`/patients/${patient.id}`)}
                className="p-4 bg-gray-50 rounded-xl border border-gray-200 hover:bg-blue-50 hover:border-blue-200 cursor-pointer transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-semibold shadow-md group-hover:scale-110 transition-transform">
                    {patient.name.charAt(0)}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">{patient.name}</p>
                    <p className="text-xs text-gray-600">{patient.age} Years old</p>
                  </div>
                  <span className="text-xs font-semibold text-blue-600">{patient.time}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-200 text-center">
              <p className="text-sm text-gray-500">No patients scheduled for today</p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="mt-4 flex gap-2">
          <button className="flex-1 p-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
            <svg className="w-5 h-5 text-gray-600 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </button>
          <button className="flex-1 p-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
            <svg className="w-5 h-5 text-gray-600 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          </button>
          <button className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-semibold text-sm hover:from-blue-700 hover:to-indigo-700 transition-all shadow hover:shadow-md">
            Book Consultations
          </button>
        </div>
      </div>
    </aside>
  );
}

