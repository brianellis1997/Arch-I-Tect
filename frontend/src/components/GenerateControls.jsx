/**
 * GenerateControls component for configuring and triggering code generation.
 * 
 * Allows users to select the output format and initiate the IaC
 * generation process.
 */

 import React from 'react';
 import { Sparkles, FileCode, Cloud } from 'lucide-react';
 import toast from 'react-hot-toast';
 import clsx from 'clsx';
 
 import useAppStore from '../store/appStore';
 import { generateCode } from '../services/api';
 
 const GenerateControls = () => {
   const {
     imageId,
     outputFormat,
     isGenerating,
     canGenerate,
     setOutputFormat,
     setIsGenerating,
     setGeneratedCode,
     setError,
   } = useAppStore();
   
   /**
    * Handle code generation.
    */
   const handleGenerate = async () => {
     if (!canGenerate()) return;
     
     try {
       setIsGenerating(true);
       setError(null);
       
       // Clear previous results
       setGeneratedCode('', '', []);
       
       // Generate code
       const response = await generateCode(imageId, outputFormat, true);
       
       // Update store with results
       setGeneratedCode(
         response.code,
         response.explanation,
         response.detected_resources
       );
       
       toast.success(`${outputFormat === 'terraform' ? 'Terraform' : 'CloudFormation'} code generated successfully!`);
     } catch (error) {
       console.error('Generation failed:', error);
       setError(error.message);
       toast.error('Failed to generate code. Please try again.');
     } finally {
       setIsGenerating(false);
     }
   };
   
   return (
     <div className="bg-white rounded-lg shadow-md p-6">
       <h3 className="text-lg font-semibold text-gray-900 mb-4">Generation Options</h3>
       
       {/* Output Format Selection */}
       <div className="mb-6">
         <label className="block text-sm font-medium text-gray-700 mb-3">
           Output Format
         </label>
         
         <div className="grid grid-cols-2 gap-3">
           <button
             onClick={() => setOutputFormat('terraform')}
             disabled={isGenerating}
             className={clsx(
               'relative flex items-center justify-center gap-2 px-4 py-3 rounded-lg border-2 transition-all',
               'hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
               {
                 'border-primary bg-primary/5 text-primary': outputFormat === 'terraform',
                 'border-gray-200 bg-white text-gray-700 hover:border-gray-300': outputFormat !== 'terraform',
                 'opacity-50 cursor-not-allowed': isGenerating,
               }
             )}
           >
             <FileCode className="w-5 h-5" />
             <span className="font-medium">Terraform</span>
             {outputFormat === 'terraform' && (
               <div className="absolute top-2 right-2">
                 <div className="w-2 h-2 bg-primary rounded-full" />
               </div>
             )}
           </button>
           
           <button
             onClick={() => setOutputFormat('cloudformation')}
             disabled={isGenerating}
             className={clsx(
               'relative flex items-center justify-center gap-2 px-4 py-3 rounded-lg border-2 transition-all',
               'hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
               {
                 'border-primary bg-primary/5 text-primary': outputFormat === 'cloudformation',
                 'border-gray-200 bg-white text-gray-700 hover:border-gray-300': outputFormat !== 'cloudformation',
                 'opacity-50 cursor-not-allowed': isGenerating,
               }
             )}
           >
             <Cloud className="w-5 h-5" />
             <span className="font-medium">CloudFormation</span>
             {outputFormat === 'cloudformation' && (
               <div className="absolute top-2 right-2">
                 <div className="w-2 h-2 bg-primary rounded-full" />
               </div>
             )}
           </button>
         </div>
       </div>
       
       {/* Generate Button */}
       <button
         onClick={handleGenerate}
         disabled={!canGenerate() || isGenerating}
         className={clsx(
           'w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium transition-all',
           'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
           {
             'bg-primary text-white hover:bg-primary-dark shadow-lg hover:shadow-xl transform hover:-translate-y-0.5':
               canGenerate() && !isGenerating,
             'bg-gray-100 text-gray-400 cursor-not-allowed':
               !canGenerate() || isGenerating,
           }
         )}
       >
         <Sparkles className={clsx('w-5 h-5', { 'animate-pulse': isGenerating })} />
         <span>
           {isGenerating
             ? 'Generating...'
             : `Generate ${outputFormat === 'terraform' ? 'Terraform' : 'CloudFormation'} Code`}
         </span>
       </button>
       
       {/* Help Text */}
       <p className="mt-4 text-xs text-gray-500 text-center">
         {canGenerate()
           ? 'AI will analyze your diagram and generate Infrastructure as Code'
           : 'Upload an architecture diagram to get started'}
       </p>
     </div>
   );
 };
 
 export default GenerateControls;