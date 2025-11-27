/**
 * Image Viewer Component
 * Displays medical images with zoom/pan capabilities and AI heatmap overlay toggle
 */
'use client';

import { useState, useEffect } from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { imagingService, Imaging } from '@/lib/imagingService';
import { apiClient } from '@/lib/apiClient';

interface ImageViewerProps {
  patientId: string;
}

interface ImageAnalysis {
  version: string;
  abnormality_score: number;
  classification: string;
  heatmap_url?: string;
  explanation: string;
}

export function ImageViewer({ patientId }: ImageViewerProps) {
  const [images, setImages] = useState<Imaging[]>([]);
  const [selectedImage, setSelectedImage] = useState<Imaging | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [imageAnalysis, setImageAnalysis] = useState<ImageAnalysis | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  useEffect(() => {
    fetchImages();
  }, [patientId]);

  useEffect(() => {
    if (selectedImage) {
      fetchImageFile(selectedImage.id);
      // TODO: Fetch AI analysis when image analysis service is available (Task 16)
      // fetchImageAnalysis(selectedImage.id);
    }
  }, [selectedImage]);

  const fetchImages = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await imagingService.getPatientImages(patientId);
      setImages(response.items);
      if (response.items.length > 0) {
        setSelectedImage(response.items[0]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load images');
      console.error('Error fetching images:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchImageFile = async (imageId: string) => {
    try {
      // Get image file from backend
      const response = await apiClient.get(`/imaging/file/${imageId}`, {
        responseType: 'blob',
      }) as any; // Type assertion needed for blob response
      
      const url = URL.createObjectURL(response.data);
      setImageUrl(url);
    } catch (err) {
      console.error('Error fetching image file:', err);
      setError('Failed to load image file');
    }
  };

  // TODO: Implement when image analysis service is available (Task 16)
  const fetchImageAnalysis = async (imageId: string) => {
    setLoadingAnalysis(true);
    try {
      // This will be implemented when Task 18 (AI Service Routing) is complete
      // const response = await apiClient.post(`/ai/image-analysis`, {
      //   image_id: imageId,
      //   image_type: selectedImage?.type,
      // });
      // setImageAnalysis(response.data);
    } catch (err) {
      console.error('Error fetching image analysis:', err);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const handleImageSelect = (image: Imaging) => {
    setSelectedImage(image);
    setShowHeatmap(false);
    setImageAnalysis(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading images...</p>
        </div>
      </div>
    );
  }

  if (error && images.length === 0) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchImages}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-500">No medical images available for this patient.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-xl border border-gray-200 p-6">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
            <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Medical Imaging</h2>
        </div>
        
        {/* Image List */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Image ({images.length} available)
          </label>
          <div className="flex flex-wrap gap-2">
            {images.map((image) => (
              <button
                key={image.id}
                onClick={() => handleImageSelect(image)}
                className={`
                  px-4 py-2 rounded-md text-sm font-medium transition-colors
                  ${
                    selectedImage?.id === image.id
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                {image.type} - {new Date(image.created_at).toLocaleDateString()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {selectedImage && (
        <div className="space-y-4">
          {/* Image Controls */}
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <div>
                <span className="text-sm font-medium text-gray-700">Type: </span>
                <span className="text-sm text-gray-900">{selectedImage.type}</span>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Date: </span>
                <span className="text-sm text-gray-900">
                  {new Date(selectedImage.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showHeatmap}
                  onChange={(e) => setShowHeatmap(e.target.checked)}
                  disabled={!imageAnalysis?.heatmap_url}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-sm text-gray-700">Show AI Heatmap</span>
                {!imageAnalysis?.heatmap_url && (
                  <span className="text-xs text-gray-500">(Analysis not available)</span>
                )}
              </label>
            </div>
          </div>

          {/* Image Viewer */}
          <div className="border border-gray-300 rounded-lg bg-gray-100 p-4 min-h-[400px] relative">
            {imageUrl ? (
              <TransformWrapper
                initialScale={1}
                minScale={0.5}
                maxScale={4}
                wheel={{ step: 0.1 }}
                doubleClick={{ disabled: false }}
                panning={{ disabled: false }}
              >
                {({ zoomIn, zoomOut, resetTransform }) => (
                  <>
                    <div className="absolute top-6 right-6 z-10 flex gap-2">
                      <button
                        onClick={() => zoomIn()}
                        className="px-3 py-1 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 shadow"
                        title="Zoom In"
                      >
                        +
                      </button>
                      <button
                        onClick={() => zoomOut()}
                        className="px-3 py-1 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 shadow"
                        title="Zoom Out"
                      >
                        −
                      </button>
                      <button
                        onClick={() => resetTransform()}
                        className="px-3 py-1 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 shadow"
                        title="Reset"
                      >
                        Reset
                      </button>
                    </div>
                    <TransformComponent wrapperClass="flex items-center justify-center min-h-[400px]">
                      <div className="relative">
                        <img
                          src={imageUrl}
                          alt={`${selectedImage.type} - ${selectedImage.id}`}
                          className="max-w-full max-h-[600px] object-contain"
                        />
                        {showHeatmap && imageAnalysis?.heatmap_url && (
                          <img
                            src={imageAnalysis.heatmap_url}
                            alt="AI Heatmap Overlay"
                            className="absolute top-0 left-0 w-full h-full opacity-50 pointer-events-none"
                          />
                        )}
                      </div>
                    </TransformComponent>
                  </>
                )}
              </TransformWrapper>
            ) : (
              <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Loading image...</p>
                </div>
              </div>
            )}
          </div>

          {/* AI Analysis Info */}
          {imageAnalysis && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-2 mb-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  Experimental
                </span>
                <span className="text-sm font-medium text-blue-900">AI Analysis</span>
              </div>
              <div className="space-y-2 text-sm text-blue-800">
                <div>
                  <span className="font-medium">Classification: </span>
                  <span className="capitalize">{imageAnalysis.classification}</span>
                </div>
                <div>
                  <span className="font-medium">Abnormality Score: </span>
                  <span>{(imageAnalysis.abnormality_score * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="font-medium">Explanation: </span>
                  <span>{imageAnalysis.explanation}</span>
                </div>
                <div className="text-xs text-blue-600 mt-2">
                  Model Version: {imageAnalysis.version}
                </div>
              </div>
            </div>
          )}

          {!imageAnalysis && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-600">
                AI analysis not available. Image analysis service will be implemented in Task 16.
              </p>
            </div>
          )}

          {/* Instructions */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600">
              <strong>Controls:</strong> Use mouse wheel to zoom, click and drag to pan, double-click to reset.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

