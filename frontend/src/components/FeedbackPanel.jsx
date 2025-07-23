/**
 * FeedbackPanel component for displaying analysis results.
 * 
 * Shows the LLM's explanation of the architecture and lists
 * all detected cloud resources from the diagram.
 */

 import React from 'react';
 import { MessageSquare, Server, CheckCircle2, AlertCircle } from 'lucide-react';
 import clsx from 'clsx';
 
 import useAppStore from '../store/appStore';
 
 const FeedbackPanel = () => {
   const { codeExplanation, detectedResources, generatedCode } = useAppStore();
   
   if (!generatedCode || (!codeExplanation && detectedResources.length === 0)) {
     return null;
   }
   
   /**
    * Get icon for resource type.
    */
   const getResourceIcon = (resource) => {
     // In a real app, you might have specific icons for each AWS service
     return <Server className="w-4 h-4" />;
   };
   
   /**
    * Format resource name for display.
    */
   const formatResourceName = (resource) => {
     // Convert technical names to readable format
     const formatted = resource
       .replace(/^aws_/, '')
       .replace(/_/g, ' ')
       .replace(/\b\w/g, (l) => l.toUpperCase());
     
     return formatted;
   };
   
   return (
     <div className="space-y-4">
       {/* Detected Resources */}
       {detectedResources.length > 0 && (
         <div className="bg-white rounded-lg shadow-md overflow-hidden">
           <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
             <div className="flex items-center gap-2">
               <CheckCircle2 className="w-5 h-5 text-green-600" />
               <h3 className="font-medium text-gray-900">
                 Detected Resources ({detectedResources.length})
               </h3>
             </div>
           </div>
           
           <div className="p-4">
             <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
               {detectedResources.map((resource, index) => (
                 <div
                   key={index}
                   className={clsx(
                     'flex items-center gap-2 px-3 py-2 rounded-md',
                     'bg-gray-50 border border-gray-200',
                     'hover:bg-gray-100 transition-colors'
                   )}
                 >
                   <div className="text-gray-600">
                     {getResourceIcon(resource)}
                   </div>
                   <span className="text-sm font-medium text-gray-700">
                     {formatResourceName(resource)}
                   </span>
                 </div>
               ))}
             </div>
             
             <div className="mt-4 flex items-start gap-2">
               <AlertCircle className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
               <p className="text-xs text-gray-600">
                 These resources were identified in your diagram. Please review the generated
                 code to ensure all configurations match your requirements.
               </p>
             </div>
           </div>
         </div>
       )}
       
       {/* Architecture Explanation */}
       {codeExplanation && (
         <div className="bg-white rounded-lg shadow-md overflow-hidden">
           <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
             <div className="flex items-center gap-2">
               <MessageSquare className="w-5 h-5 text-blue-600" />
               <h3 className="font-medium text-gray-900">Architecture Analysis</h3>
             </div>
           </div>
           
           <div className="p-4">
             <div className="prose prose-sm max-w-none text-gray-700">
               {codeExplanation.split('\n\n').map((paragraph, index) => (
                 <p key={index} className="mb-3 last:mb-0">
                   {paragraph}
                 </p>
               ))}
             </div>
           </div>
         </div>
       )}
     </div>
   );
 };
 
 export default FeedbackPanel;