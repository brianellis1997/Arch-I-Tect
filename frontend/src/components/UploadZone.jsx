/**
 * UploadZone component for drag-and-drop file uploads.
 * 
 * Provides an intuitive interface for users to upload architecture
 * diagram images via drag-and-drop or file selection.
 */

 import React, { useCallback, useState } from 'react';
 import { useDropzone } from 'react-dropzone';
 import { Upload, Image, AlertCircle, Loader2 } from 'lucide-react';
 import toast from 'react-hot-toast';
 import clsx from 'clsx';
 
 import useAppStore from '../store/appStore';
 import { uploadImage } from '../services/api';
 
 const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
 const ACCEPTED_TYPES = {
   'image/png': ['.png'],
   'image/jpeg': ['.jpg', '.jpeg'],
   'image/webp': ['.webp'],
 };
 
 const UploadZone = () => {
   const {
     isUploading,
     uploadProgress,
     setUploadedImage,
     setIsUploading,
     setUploadProgress,
     clearError,
   } = useAppStore();
   
   const [dragActive, setDragActive] = useState(false);
   
   /**
    * Handle file drop or selection.
    */
   const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
     // Handle rejected files
     if (rejectedFiles.length > 0) {
       const error = rejectedFiles[0].errors[0];
       toast.error(error.message);
       return;
     }
     
     if (acceptedFiles.length === 0) return;
     
     const file = acceptedFiles[0];
     
     // Validate file size
     if (file.size > MAX_FILE_SIZE) {
       toast.error(`File size must be less than ${MAX_FILE_SIZE / 1024 / 1024}MB`);
       return;
     }
     
     try {
       setIsUploading(true);
       setUploadProgress(0);
       clearError();
       
       // Simulate upload progress (since we can't track actual progress with FormData)
       const progressInterval = setInterval(() => {
         setUploadProgress((prev) => {
           if (prev >= 90) {
             clearInterval(progressInterval);
             return prev;
           }
           return prev + 10;
         });
       }, 200);
       
       // Upload the file
       const response = await uploadImage(file);
       
       clearInterval(progressInterval);
       setUploadProgress(100);
       
       // Store the uploaded image info
       setUploadedImage(
         file,
         response.image_id,
         response.metadata,
         response.preview_url
       );
       
       toast.success('Image uploaded successfully!');
     } catch (error) {
       console.error('Upload failed:', error);
       toast.error('Failed to upload image. Please try again.');
     } finally {
       setIsUploading(false);
       setUploadProgress(0);
     }
   }, [setUploadedImage, setIsUploading, setUploadProgress, clearError]);
   
   /**
    * Configure dropzone behavior.
    */
   const { getRootProps, getInputProps, isDragActive } = useDropzone({
     onDrop,
     accept: ACCEPTED_TYPES,
     maxFiles: 1,
     disabled: isUploading,
     onDragEnter: () => setDragActive(true),
     onDragLeave: () => setDragActive(false),
     onDropAccepted: () => setDragActive(false),
     onDropRejected: () => setDragActive(false),
   });
   
   return (
     <div
       {...getRootProps()}
       className={clsx(
         'relative border-2 border-dashed rounded-lg p-8 transition-all duration-200 cursor-pointer',
         'hover:border-primary hover:bg-primary/5',
         {
           'border-primary bg-primary/10': isDragActive || dragActive,
           'border-gray-300 bg-white': !isDragActive && !dragActive,
           'opacity-50 cursor-not-allowed': isUploading,
         }
       )}
     >
       <input {...getInputProps()} />
       
       {/* Upload Progress Overlay */}
       {isUploading && (
         <div className="absolute inset-0 bg-white/80 flex items-center justify-center rounded-lg">
           <div className="text-center">
             <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
             <p className="text-sm text-gray-600">Uploading... {uploadProgress}%</p>
             <div className="w-48 h-2 bg-gray-200 rounded-full mt-2 overflow-hidden">
               <div
                 className="h-full bg-primary transition-all duration-300"
                 style={{ width: `${uploadProgress}%` }}
               />
             </div>
           </div>
         </div>
       )}
       
       {/* Upload Instructions */}
       {!isUploading && (
         <div className="text-center">
           <div className="flex justify-center mb-4">
             {isDragActive || dragActive ? (
               <Image className="w-16 h-16 text-primary animate-pulse" />
             ) : (
               <Upload className="w-16 h-16 text-gray-400" />
             )}
           </div>
           
           <p className="text-lg font-medium text-gray-700 mb-2">
             {isDragActive || dragActive
               ? 'Drop your diagram here'
               : 'Drag & drop your architecture diagram'}
           </p>
           
           <p className="text-sm text-gray-500 mb-4">
             or <span className="text-primary font-medium">browse files</span>
           </p>
           
           <div className="flex items-center justify-center gap-2 text-xs text-gray-400">
             <AlertCircle className="w-4 h-4" />
             <span>PNG, JPG, JPEG, WebP up to 10MB</span>
           </div>
         </div>
       )}
     </div>
   );
 };
 
 export default UploadZone;