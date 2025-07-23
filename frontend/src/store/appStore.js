/**
 * Global application state management using Zustand.
 * 
 * This store manages the entire application state including
 * uploaded images, generated code, and UI states.
 */

 import { create } from 'zustand';
 import { devtools } from 'zustand/middleware';
 
 const useAppStore = create(
   devtools(
     (set, get) => ({
       // Image state
       uploadedImage: null,
       imageId: null,
       imageMetadata: null,
       previewUrl: null,
       
       // Generation state
       generatedCode: '',
       codeExplanation: '',
       detectedResources: [],
       outputFormat: 'terraform',
       
       // UI state
       isUploading: false,
       isGenerating: false,
       uploadProgress: 0,
       error: null,
       
       // Actions
       setUploadedImage: (file, imageId, metadata, previewUrl) => set({
         uploadedImage: file,
         imageId,
         imageMetadata: metadata,
         previewUrl,
         error: null,
       }),
       
       clearUploadedImage: () => set({
         uploadedImage: null,
         imageId: null,
         imageMetadata: null,
         previewUrl: null,
         generatedCode: '',
         codeExplanation: '',
         detectedResources: [],
       }),
       
       setGeneratedCode: (code, explanation, resources) => set({
         generatedCode: code,
         codeExplanation: explanation,
         detectedResources: resources,
       }),
       
       setOutputFormat: (format) => set({ outputFormat: format }),
       
       setIsUploading: (isUploading) => set({ isUploading }),
       setIsGenerating: (isGenerating) => set({ isGenerating }),
       setUploadProgress: (progress) => set({ uploadProgress: progress }),
       setError: (error) => set({ error }),
       clearError: () => set({ error: null }),
       
       // Computed values
       hasImage: () => {
         const state = get();
         return !!state.imageId;
       },
       
       hasGeneratedCode: () => {
         const state = get();
         return !!state.generatedCode;
       },
       
       canGenerate: () => {
         const state = get();
         return state.hasImage() && !state.isGenerating;
       },
     }),
     {
       name: 'arch-i-tect-store',
     }
   )
 );
 
 export default useAppStore;