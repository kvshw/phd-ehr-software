/**
 * Synthetic Data Generator Component
 * Allows admins to generate synthetic test data
 */
'use client';

import { useState } from 'react';
import { adminService } from '@/lib/adminService';

export function SyntheticDataGenerator() {
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [options, setOptions] = useState({
    num_patients: 10,
    num_vitals_per_patient: 5,
    num_labs_per_patient: 3,
    num_images_per_patient: 2,
  });

  const handleGenerate = async () => {
    if (!confirm('This will generate synthetic data. Continue?')) {
      return;
    }

    setGenerating(true);
    setError(null);
    setResult(null);

    try {
      const response = await adminService.generateSyntheticData(options);
      setResult(`Successfully generated: ${JSON.stringify(response.generated, null, 2)}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate synthetic data');
      console.error('Error generating synthetic data:', err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Synthetic Data Generator</h3>
      <p className="text-sm text-gray-600 mb-6">
        Generate synthetic test data for research purposes. All data is anonymized and contains no PHI.
      </p>

      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Number of Patients
          </label>
          <input
            type="number"
            min="1"
            max="100"
            value={options.num_patients}
            onChange={(e) =>
              setOptions({ ...options, num_patients: parseInt(e.target.value) || 0 })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Vitals per Patient
          </label>
          <input
            type="number"
            min="1"
            max="50"
            value={options.num_vitals_per_patient}
            onChange={(e) =>
              setOptions({ ...options, num_vitals_per_patient: parseInt(e.target.value) || 0 })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Labs per Patient
          </label>
          <input
            type="number"
            min="1"
            max="50"
            value={options.num_labs_per_patient}
            onChange={(e) =>
              setOptions({ ...options, num_labs_per_patient: parseInt(e.target.value) || 0 })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Images per Patient
          </label>
          <input
            type="number"
            min="0"
            max="20"
            value={options.num_images_per_patient}
            onChange={(e) =>
              setOptions({ ...options, num_images_per_patient: parseInt(e.target.value) || 0 })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {result && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-800 whitespace-pre-wrap">{result}</p>
        </div>
      )}

      <button
        onClick={handleGenerate}
        disabled={generating}
        className={`w-full px-4 py-2 rounded-md text-sm font-medium ${
          generating
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-indigo-600 hover:bg-indigo-700'
        } text-white`}
      >
        {generating ? 'Generating...' : 'Generate Synthetic Data'}
      </button>
    </div>
  );
}

