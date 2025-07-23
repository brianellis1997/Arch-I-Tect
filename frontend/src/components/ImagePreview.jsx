/**
 * ImagePreview component for displaying uploaded architecture diagrams.
 * 
 * Shows the uploaded image with metadata and provides options to
 * view fullscreen or remove the image.
 */

 import React, { useState } from 'react';
 import { X, Maximize2, Info, Image as ImageIcon } from 'lucide-react';
 import clsx from 'clsx';
 
 import useAppStore from '../store/appStore';
 
 const ImagePreview = () => {
   const {
     uploadedImage,
     imageMetadata,
     previewUrl,
     clearUploadedImage,
   } = useAppStore();
   
   const [showFullscreen, setShowFullscreen] = useState(false);
   const [imageError, setImageError] = useState(false);
   
   if (!uploadedImage || !previewUrl) {
     return null;
   }
   
   /**
    * Format file size for display.
    */
   const formatFileSize = (bytes) => {
     if (bytes < 1024) return `${bytes} B`;
     if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
     return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
   };
   
   return (
     <>
       <div className="bg-white rounded-lg shadow-md overflow-hidden">
         {/* Header */}
         <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
           <div className="flex items-center gap-2">
             <ImageIcon className="w-5 h-5 text-gray-600" />
             <h3 className="font-medium text-gray-900">Uploaded Diagram</h3>
           </div>
           
           <div className="flex items-center gap-2">
             <button
               onClick={() => setShowFullscreen(true)}
               className="p-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
               title="View fullscreen"
             >
               <Maximize2 className="w-4 h-4" />
             </button>
             
             <button
               onClick={clearUploadedImage}
               className="p-1.5 text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
               title="Remove image"
             >
               <X className="w-4 h-4" />
             </button>
           </div>
         </div>
         
         {/* Image Container */}
         <div className="relative bg-gray-100 aspect-video">
           {imageError ? (
             <div className="absolute inset-0 flex items-center justify-center">
               <div className="text-center">
                 <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                 <p className="text-sm text-gray-500">Failed to load image</p>
               </div>
             </div>
           ) : (
             <img
               src={previewUrl}
               alt="Architecture diagram"
               className="w-full h-full object-contain"
               onError={() => setImageError(true)}
             />
           )}
         </div>
         
         {/* Metadata */}
         {imageMetadata && (
           <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
             <div className="flex items-start gap-2">
               <Info className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
               <div className="text-xs text-gray-600 space-y-1">
                 <p>
                   <span className="font-medium">Name:</span> {uploadedImage.name}
                 </p>
                 <p>
                   <span className="font-medium">Size:</span>{' '}
                   {formatFileSize(uploadedImage.size)} ({imageMetadata.width} x{' '}
                   {imageMetadata.height}px)
                 </p>
                 <p>
                   <span className="font-medium">Format:</span> {imageMetadata.format || 'Unknown'}
                 </p>
               </div>
             </div>
           </div>
         )}
       </div>
       
       {/* Fullscreen Modal */}
       {showFullscreen && (
         <div
           className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
           onClick={() => setShowFullscreen(false)}
         >
           <button
             className="absolute top-4 right-4 p-2 text-white hover:bg-white/10 rounded-lg transition-colors"
             onClick={() => setShowFullscreen(false)}
           >
             <X className="w-6 h-6" />
           </button>
           
           <img
             src={previewUrl}
             alt="Architecture diagram fullscreen"
             className="max-w-full max-h-full object-contain"
             onClick={(e) => e.stopPropagation()}
           />
         </div>
       )}
     </>
   );
 };
 
 export default ImagePreview;