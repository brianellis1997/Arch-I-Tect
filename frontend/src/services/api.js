/**
 * API service for interacting with the Arch-I-Tect backend.
 * 
 * This module provides a clean interface for all API operations,
 * handling errors and response formatting consistently.
 */

 import axios from 'axios';
 import toast from 'react-hot-toast';
 
 // Create axios instance with default config
 const api = axios.create({
   baseURL: '/api/v1',
   timeout: 300000, // 5 minutes for large file uploads and processing
   headers: {
     'Content-Type': 'application/json',
   },
 });
 
 // Request interceptor for logging
 api.interceptors.request.use(
   (config) => {
     console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
     return config;
   },
   (error) => {
     console.error('[API] Request error:', error);
     return Promise.reject(error);
   }
 );
 
 // Response interceptor for error handling
 api.interceptors.response.use(
   (response) => {
     console.log(`[API] Response ${response.status}:`, response.data);
     return response;
   },
   (error) => {
     const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
     console.error('[API] Response error:', errorMessage);
     
     // Show error toast for user-facing errors
     if (error.response?.status !== 404) {
       toast.error(errorMessage);
     }
     
     return Promise.reject(error);
   }
 );
 
 /**
  * Upload an architecture diagram image.
  * 
  * @param {File} file - The image file to upload
  * @returns {Promise<Object>} Upload response with image_id and metadata
  */
 export const uploadImage = async (file) => {
   const formData = new FormData();
   formData.append('file', file);
   
   const response = await api.post('/upload', formData, {
     headers: {
       'Content-Type': 'multipart/form-data',
     },
   });
   
   return response.data;
 };
 
 /**
  * Generate Infrastructure as Code from an uploaded diagram.
  * 
  * @param {string} imageId - ID of the uploaded image
  * @param {string} outputFormat - 'terraform' or 'cloudformation'
  * @param {boolean} includeExplanation - Whether to include architectural explanation
  * @returns {Promise<Object>} Generated code and metadata
  */
 export const generateCode = async (imageId, outputFormat = 'terraform', includeExplanation = true) => {
   const response = await api.post('/generate', {
     image_id: imageId,
     output_format: outputFormat,
     include_explanation: includeExplanation,
   });
   
   return response.data;
 };
 
 /**
  * Get the preview URL for an uploaded image.
  * 
  * @param {string} imageId - ID of the uploaded image
  * @returns {string} Preview URL
  */
 export const getPreviewUrl = (imageId) => {
   return `/api/v1/preview/${imageId}`;
 };
 
 /**
  * Check the processing status of an uploaded image.
  * 
  * @param {string} imageId - ID of the uploaded image
  * @returns {Promise<Object>} Status information
  */
 export const checkStatus = async (imageId) => {
   const response = await api.get(`/status/${imageId}`);
   return response.data;
 };
 
 /**
  * Health check to verify backend connectivity.
  * 
  * @returns {Promise<boolean>} True if backend is healthy
  */
 export const healthCheck = async () => {
   try {
     const response = await api.get('/health');
     return response.status === 200;
   } catch (error) {
     return false;
   }
 };
 
 // Export the api instance for custom requests
 export default api;